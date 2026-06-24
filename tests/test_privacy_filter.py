"""Tests for src.privacy_filter — PHI/PII redaction before cloud LLM calls."""

import os
from copy import deepcopy

import pytest

from src.privacy_filter import (
    is_local_llm_url,
    maybe_redact_messages_for_endpoint,
    privacy_filter_enabled,
    redact_messages,
    redact_text,
)


class TestPrivacyFilterEnabled:
    def test_default_enabled(self, monkeypatch):
        monkeypatch.delenv("RAPHA_PRIVACY_FILTER", raising=False)
        assert privacy_filter_enabled() is True

    @pytest.mark.parametrize("value", ("0", "false", "no", "off", "FALSE"))
    def test_disabled_values(self, monkeypatch, value):
        monkeypatch.setenv("RAPHA_PRIVACY_FILTER", value)
        assert privacy_filter_enabled() is False

    def test_explicit_true(self, monkeypatch):
        monkeypatch.setenv("RAPHA_PRIVACY_FILTER", "true")
        assert privacy_filter_enabled() is True


class TestIsLocalLlmUrl:
    @pytest.mark.parametrize(
        "url",
        (
            "",
            "http://127.0.0.1:11434/api/generate",
            "http://localhost:7000/v1/chat/completions",
            "http://[::1]:8080/v1",
            "ollama://llama3",
            "http://0.0.0.0:11434",
        ),
    )
    def test_local_urls(self, url):
        assert is_local_llm_url(url) is True

    @pytest.mark.parametrize(
        "url",
        (
            "https://api.openai.com/v1/chat/completions",
            "https://api.anthropic.com/v1/messages",
            "http://192.168.1.10:8080/v1",
        ),
    )
    def test_remote_urls(self, url):
        assert is_local_llm_url(url) is False

    def test_lan_ollama_port_treated_as_local(self):
        # Ollama default port on LAN is still considered local inference.
        assert is_local_llm_url("http://192.168.1.10:11434/v1") is True


class TestRedactText:
    def test_curp_redacted(self):
        text = "Paciente CURP GODE561231HMCRRL09 acude a consulta."
        out, count = redact_text(text)
        assert "[REDACTED:curp]" in out
        assert "GODE561231HMCRRL09" not in out
        assert count >= 1

    def test_email_redacted(self):
        text = "Contacto: maria.garcia@hospital.mx"
        out, count = redact_text(text)
        assert "[REDACTED:email]" in out
        assert "maria.garcia@hospital.mx" not in out
        assert count == 1

    def test_phone_redacted(self):
        text = "Tel: +52 55 1234 5678"
        out, count = redact_text(text)
        assert "[REDACTED:phone]" in out
        assert count >= 1

    def test_medical_record_redacted(self):
        text = "Expediente HC 1234"
        out, count = redact_text(text)
        assert "[REDACTED:medical_record]" in out
        assert count >= 1

    def test_empty_and_none(self):
        assert redact_text("") == ("", 0)
        assert redact_text(None) == (None, 0)

    def test_no_identifiers_unchanged(self):
        text = "Nota clínica sin identificadores personales."
        out, count = redact_text(text)
        assert out == text
        assert count == 0


class TestRedactMessages:
    def test_string_content_redacted(self):
        messages = [{"role": "user", "content": "Email: test@example.com"}]
        out, count = redact_messages(messages)
        assert out[0]["content"] == "Email: [REDACTED:email]"
        assert count == 1
        assert messages[0]["content"] == "Email: test@example.com"

    def test_multipart_content_redacted(self):
        messages = [{
            "role": "user",
            "content": [{"type": "text", "text": "CURP GODE561231HMCRRL09"}],
        }]
        out, count = redact_messages(messages)
        assert "[REDACTED:curp]" in out[0]["content"][0]["text"]
        assert count >= 1

    def test_empty_messages(self):
        assert redact_messages([]) == ([], 0)


class TestMaybeRedactMessagesForEndpoint:
    def test_skips_local_endpoint(self, monkeypatch):
        monkeypatch.setenv("RAPHA_PRIVACY_FILTER", "true")
        messages = [{"role": "user", "content": "test@example.com"}]
        result = maybe_redact_messages_for_endpoint(
            "http://127.0.0.1:11434/v1", messages,
        )
        assert result is messages
        assert "test@example.com" in result[0]["content"]

    def test_redacts_cloud_endpoint(self, monkeypatch):
        monkeypatch.setenv("RAPHA_PRIVACY_FILTER", "true")
        messages = [{"role": "user", "content": "test@example.com"}]
        result = maybe_redact_messages_for_endpoint(
            "https://api.openai.com/v1/chat/completions", messages,
        )
        assert result is not messages
        assert "[REDACTED:email]" in result[0]["content"]

    def test_log_contains_counts_but_never_phi(self, monkeypatch, caplog):
        monkeypatch.setenv("RAPHA_PRIVACY_FILTER", "true")
        secret = "patient@example.com"
        messages = [{"role": "user", "content": secret}]
        with caplog.at_level("INFO", logger="src.privacy_filter"):
            maybe_redact_messages_for_endpoint("https://api.example/v1", messages)
        assert "email=1" in caplog.text
        assert secret not in caplog.text

    def test_disabled_filter_skips_redaction(self, monkeypatch):
        monkeypatch.setenv("RAPHA_PRIVACY_FILTER", "false")
        messages = [{"role": "user", "content": "test@example.com"}]
        result = maybe_redact_messages_for_endpoint(
            "https://api.openai.com/v1/chat/completions", messages,
        )
        assert result is messages
