"""Regex-based PHI/PII redaction before cloud LLM calls (Mexico-focused).

Inspired by OpenDoctor privacy-filter; deterministic first pass only.
Local/self-hosted endpoints are not redacted — data stays on your machine.
"""

from __future__ import annotations

import os
import re
from copy import deepcopy
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse

# Mexican health & contact identifiers (subset of OpenDoctor patterns)
_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    ("curp", re.compile(
        r"\b[A-Z]{4}\d{6}[HM](?:AS|BS|CS|CL|CC|CN|CH|DF|DG|GT|GR|HG|JC|MC|MN|MS|NT|NE|OC|PL|QH|QR|SP|SL|SR|TC|TL|TS|VZ|YN|ZS)[A-Z]{3}[0-9A-Z]\d\b",
        re.IGNORECASE,
    )),
    ("rfc", re.compile(r"\b[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}\b", re.IGNORECASE)),
    ("nss", re.compile(r"\b\d{11}\b")),
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("phone", re.compile(
        r"(?:\+52[\s-]?)?(?:\(\d{2,4}\)|\d{2,4})[\s-]?\d{2,4}[\s-]?\d{2,4}[\s-]?\d{2,4}",
    )),
    ("medical_record", re.compile(
        r"\b(?:EXP|MRN|HC|HISTORIA|REG(?:ISTRO)?)[\s:-]*\d{4,10}\b",
        re.IGNORECASE,
    )),
]

_REDACT_FMT = "[REDACTED:{tag}]"


def privacy_filter_enabled() -> bool:
    return os.environ.get("RAPHA_PRIVACY_FILTER", "true").strip().lower() not in {
        "0", "false", "no", "off",
    }


def is_local_llm_url(url: str) -> bool:
    """True when inference stays on loopback / native Ollama."""
    if not url:
        return True
    raw = url.strip().lower()
    if raw.startswith("ollama://") or ":11434" in raw:
        return True
    try:
        host = (urlparse(url).hostname or "").lower().rstrip(".")
    except Exception:
        return False
    return host in {"localhost", "127.0.0.1", "::1", "0.0.0.0"}


def _redact_text_with_stats(text: str) -> Tuple[str, Dict[str, int]]:
    if not text or not isinstance(text, str):
        return text, {}
    stats: Dict[str, int] = {}
    out = text
    for tag, pattern in _PATTERNS:
        count = len(pattern.findall(out))
        if count:
            stats[tag] = stats.get(tag, 0) + count
        out = pattern.sub(_REDACT_FMT.format(tag=tag), out)
    return out, stats


def redact_text(text: str) -> Tuple[str, int]:
    """Return redacted text and total match count."""
    redacted, stats = _redact_text_with_stats(text)
    return redacted, sum(stats.values())


def _redact_content(content: Any) -> Tuple[Any, int]:
    if isinstance(content, str):
        return redact_text(content)
    if isinstance(content, list):
        count = 0
        parts = []
        for part in content:
            if not isinstance(part, dict):
                parts.append(part)
                continue
            p = dict(part)
            if isinstance(p.get("text"), str):
                p["text"], n = redact_text(p["text"])
                count += n
            parts.append(p)
        return parts, count
    return content, 0


def redact_messages(messages: List[Dict]) -> Tuple[List[Dict], int]:
    """Deep-copy messages and redact string content for cloud providers."""
    if not messages:
        return messages, 0
    out = deepcopy(messages)
    total = 0
    for msg in out:
        if not isinstance(msg, dict):
            continue
        content = msg.get("content")
        new_content, n = _redact_content(content)
        msg["content"] = new_content
        total += n
    return out, total


def redact_messages_with_stats(messages: List[Dict]) -> Tuple[List[Dict], Dict[str, int]]:
    """Deep-copy messages and return counts by identifier category."""
    if not messages:
        return messages, {}
    out = deepcopy(messages)
    stats: Dict[str, int] = {}
    for message in out:
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if isinstance(content, str):
            message["content"], content_stats = _redact_text_with_stats(content)
        elif isinstance(content, list):
            parts = []
            content_stats = {}
            for part in content:
                if not isinstance(part, dict):
                    parts.append(part)
                    continue
                copied = dict(part)
                if isinstance(copied.get("text"), str):
                    copied["text"], part_stats = _redact_text_with_stats(copied["text"])
                    for tag, count in part_stats.items():
                        content_stats[tag] = content_stats.get(tag, 0) + count
                parts.append(copied)
            message["content"] = parts
        else:
            content_stats = {}
        for tag, count in content_stats.items():
            stats[tag] = stats.get(tag, 0) + count
    return out, stats


def maybe_redact_messages_for_endpoint(url: str, messages: List[Dict]) -> List[Dict]:
    """Apply privacy redaction when sending to non-local endpoints."""
    if not privacy_filter_enabled() or is_local_llm_url(url):
        return messages
    redacted, stats = redact_messages_with_stats(messages)
    if stats:
        import logging
        logging.getLogger(__name__).info(
            "Privacy filter redacted %d identifier span(s) before cloud LLM call (%s)",
            sum(stats.values()),
            ",".join(f"{tag}={stats[tag]}" for tag in sorted(stats)),
        )
    return redacted
