import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("skill_setup", Path(__file__).resolve().parents[1] / "skills/video-transcription/scripts/setup.py")
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


def test_reconfigure_preserves_credentials_and_custom_settings(tmp_path, monkeypatch):
    for name in ("MIMO_API_KEY", "YUANBAO_COOKIE", "XHS_COOKIE", "KUAISHOU_COOKIE", "FFMPEG_PATH"):
        monkeypatch.delenv(name, raising=False)
    path = tmp_path / "custom install" / "config.env"
    original = {"MIMO_API_KEY": "test-key", "YUANBAO_COOKIE": "hy_token=test==; hy_source=web", "FFMPEG_PATH": "C:/tools with spaces/ffmpeg.exe"}
    setup.write_config(path, original)
    assert setup.resolve_config(setup.read_config(path), False, True) == original


def test_missing_config_fails_without_prompting_in_background(monkeypatch):
    monkeypatch.delenv("MIMO_API_KEY", raising=False)
    with pytest.raises(ValueError, match="缺少 MiMo"):
        setup.resolve_config({}, False, False)


def test_reject_multiline_before_overwriting_existing_config(tmp_path):
    path = tmp_path / "config.env"
    path.write_text("MIMO_API_KEY=existing\n", encoding="utf-8")
    with pytest.raises(ValueError, match="单行"):
        setup.write_config(path, {"MIMO_API_KEY": "value\nOTHER=bad"})
    assert path.read_text(encoding="utf-8") == "MIMO_API_KEY=existing\n"


def test_setup_allows_custom_directory_with_spaces_outside_skill(tmp_path):
    target = tmp_path / "本地 转写 环境"
    assert setup.SKILL_DIR not in target.parents
