import asyncio
from types import SimpleNamespace

import httpx
import pytest

import transcribe
from app.http_client import PlatformClient
from app.parsers.xiaohongshu import _find_note


def test_xhs_selects_requested_note_not_recommendation():
    requested = {"noteId": "target", "video": {"url": "correct"}}
    recommendation = {"noteId": "other", "video": {"url": "wrong"}, "title": "more fields"}
    assert _find_note({"notes": [recommendation, requested]}, "target") is requested
    assert _find_note({"notes": [recommendation]}, "target") is None


def test_existing_output_fails_before_paid_work(tmp_path, monkeypatch, capsys):
    path = tmp_path / "existing.html"
    path.write_text("keep", encoding="utf-8")
    monkeypatch.setattr(transcribe, "load_config", lambda _: None)
    async def forbidden(_):
        pytest.fail("Existing output must be checked before any parsing or paid request")
    monkeypatch.setattr(transcribe, "process", forbidden)
    monkeypatch.setattr("sys.argv", ["transcribe", "https://v.douyin.com/example", "--output", str(path)])
    assert transcribe.main() == 1
    assert path.read_text(encoding="utf-8") == "keep"
    assert "已存在" in capsys.readouterr().err


def test_bom_config_and_trailing_equals_preserved(tmp_path, monkeypatch):
    path = tmp_path / "config.env"
    path.write_text('MIMO_API_KEY="test=="\n', encoding="utf-8-sig")
    monkeypatch.delenv("MIMO_API_KEY", raising=False)
    transcribe.load_config(path)
    assert transcribe.os.environ["MIMO_API_KEY"] == "test=="


@pytest.mark.asyncio
async def test_redirect_does_not_send_cookie_to_another_platform():
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(302, headers={"location": "https://www.douyin.com/video/1"})
    client = PlatformClient()
    await client.close()
    client.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(ValueError, match="另一个平台"):
            await client.resolve("https://www.xiaohongshu.com/explore/1", {"Cookie": "private-test"})
    finally:
        await client.close()
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_html_size_limit_is_enforced(monkeypatch):
    monkeypatch.setattr("app.http_client.settings", SimpleNamespace(request_timeout=15, max_html_bytes=10))
    client = PlatformClient()
    await client.close()
    client.client = httpx.AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(200, content=b"x" * 11)))
    try:
        with pytest.raises(ValueError, match="超过"):
            await client.get_text("https://www.douyin.com/video/1", {})
    finally:
        await client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("status,finish,hint", [(401, None, "密钥"), (402, None, "额度"), (429, None, "受限"), (200, "length", "未完整")])
async def test_mimo_errors_and_truncation_are_not_success(tmp_path, monkeypatch, status, finish, hint):
    path = tmp_path / "audio.mp3"
    path.write_bytes(b"test")
    monkeypatch.setenv("MIMO_API_KEY", "test-only")
    real_client = httpx.AsyncClient
    transport = httpx.MockTransport(lambda r: httpx.Response(status, json={"choices": [{"finish_reason": finish, "message": {"content": "partial"}}]}))
    monkeypatch.setattr(transcribe.httpx, "AsyncClient", lambda **kwargs: real_client(transport=transport, **kwargs))
    with pytest.raises(RuntimeError, match=hint):
        await transcribe.transcribe_mimo(path)
