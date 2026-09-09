#!/usr/bin/env python3
"""Run the configured installation without repeating credentials or paths."""
import json
import os
import subprocess
import sys
from pathlib import Path


def main():
    state = Path(__file__).resolve().parents[1] / "installation.json"
    if not state.exists():
        print("尚未安装转写程序，请先运行本 Skill 的 scripts/setup.py。", file=sys.stderr)
        return 1
    install = Path(json.loads(state.read_text(encoding="utf-8"))["install_dir"])
    python = install / "app" / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.is_file() or not (install / "app" / "transcribe.py").is_file():
        print("本机转写程序缺失，请重新运行 scripts/setup.py 修复安装。", file=sys.stderr)
        return 1
    return subprocess.call([str(python), str(install / "app" / "transcribe.py"), *sys.argv[1:], "--config", str(install / "config.env")])


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError):
        print("无法读取本机安装记录或启动程序，请运行 scripts/setup.py --install-dir 指定原安装目录修复。", file=sys.stderr)
        raise SystemExit(1)
