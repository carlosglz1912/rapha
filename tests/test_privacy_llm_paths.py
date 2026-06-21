"""Privacy filtering is applied on every outbound LLM transport path."""

import asyncio

import httpx

from src import llm_core


def _response(url: str) -> httpx.Response:
    request = httpx.Request("POST", url)
    return httpx.Response(
        200,
        request=request,
        json={"choices": [{"message": {"content": "ok"}}]},
    )


def test_sync_llm_path_redacts_before_transport(monkeypatch):
    captured = {}
    url = "https://sync.example/v1/chat/completions"

    def fake_post(*args, **kwargs):
        captured.update(kwargs["json"])
        return _response(url)

    monkeypatch.setenv("RAPHA_PRIVACY_FILTER", "true")
    monkeypatch.setattr(llm_core.httpx, "post", fake_post)
    result = llm_core.llm_call(
        url,
        "test-model",
        [{"role": "user", "content": "Email test@example.com"}],
    )
    assert result == "ok"
    assert captured["messages"][0]["content"] == "Email [REDACTED:email]"


def test_async_llm_path_redacts_before_transport(monkeypatch):
    captured = {}
    url = "https://async.example/v1/chat/completions"

    class FakeClient:
        async def post(self, *args, **kwargs):
            captured.update(kwargs["json"])
            return _response(url)

    monkeypatch.setenv("RAPHA_PRIVACY_FILTER", "true")
    monkeypatch.setattr(llm_core, "_get_http_client", lambda: FakeClient())
    result = asyncio.run(
        llm_core.llm_call_async(
            url,
            "test-model",
            [{"role": "user", "content": "Email test@example.com"}],
        )
    )
    assert result == "ok"
    assert captured["messages"][0]["content"] == "Email [REDACTED:email]"


def test_streaming_llm_path_redacts_before_transport(monkeypatch):
    captured = {}
    url = "https://stream.example/v1/chat/completions"

    class FakeResponse:
        status_code = 200

        async def aiter_lines(self):
            yield "data: [DONE]"

        async def aread(self):
            return b""

    class FakeContext:
        async def __aenter__(self):
            return FakeResponse()

        async def __aexit__(self, *args):
            return False

    class FakeClient:
        def stream(self, *args, **kwargs):
            captured.update(kwargs["json"])
            return FakeContext()

    monkeypatch.setenv("RAPHA_PRIVACY_FILTER", "true")
    monkeypatch.setattr(llm_core, "_get_http_client", lambda: FakeClient())

    async def consume():
        return [
            chunk
            async for chunk in llm_core.stream_llm(
                url,
                "test-model",
                [{"role": "user", "content": "Email test@example.com"}],
            )
        ]

    chunks = asyncio.run(consume())
    assert chunks
    assert captured["messages"][0]["content"] == "Email [REDACTED:email]"
