import os

import transcribe
from report import render_markdown


def test_load_config_and_render_markdown(tmp_path, monkeypatch):
    config = tmp_path / "config.env"
    config.write_text("# comment\nMIMO_API_KEY=sk-test\nXHS_COOKIE='cookie value'\n", encoding="utf-8")
    monkeypatch.delenv("MIMO_API_KEY", raising=False)

    transcribe.load_config(config)
    content = render_markdown({
        "platform": "douyin",
        "item_id": "123",
        "title": "标题\n第二行",
        "author_name": "作者",
        "source_url": "https://v.douyin.com/example",
        "transcript": "第一段。\n\n第二段。",
    })

    assert os.environ["MIMO_API_KEY"] == "sk-test"
    assert "标题 第二行" in content
    assert "- 作者：作者" in content
    assert "第一段。\n\n第二段。" in content


def test_extract_audio_passes_parser_headers_to_ffmpeg(tmp_path, monkeypatch):
    output = tmp_path / "audio.mp3"
    commands = []

    def fake_run(command, **_kwargs):
        commands.append(command)
        output.write_bytes(b"audio")
        return type("Result", (), {"returncode": 0, "stderr": ""})()

    monkeypatch.setattr(transcribe.subprocess, "run", fake_run)
    monkeypatch.setattr(transcribe, "ffmpeg_path", lambda: "ffmpeg")
    transcribe.extract_audio("https://cdn.example/video.mp4", output, {"Referer": "https://example.com/"})

    assert commands[0][commands[0].index("-headers") + 2] == "-i"
    assert "Referer: https://example.com/\r\n" in commands[0]
