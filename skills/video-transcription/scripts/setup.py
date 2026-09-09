#!/usr/bin/env python3
"""Install the bundled application and remember this user's local directory."""
from __future__ import annotations

import argparse
import getpass
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INSTALL_DIR = Path.home() / ".video-transcription"


def read_config(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.strip() and not line.lstrip().startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            values[key.strip()] = value
    return values


def write_config(path: Path, values: dict[str, str]) -> None:
    if any("\n" in value or "\r" in value for value in values.values()):
        raise ValueError("配置值必须为单行")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        if os.name != "nt":
            path.chmod(0o600)
        file.write("# 仅供本机使用，请勿提交或分享。\n")
        file.writelines(f"{key}={value}\n" for key, value in values.items())


def resolve_config(existing: dict[str, str], interactive: bool, yuanbao: bool) -> dict[str, str]:
    values = dict(existing)
    for key in ("MIMO_API_KEY", "YUANBAO_COOKIE", "XHS_COOKIE", "KUAISHOU_COOKIE", "FFMPEG_PATH"):
        if os.getenv(key, "").strip():
            values[key] = os.environ[key].strip()
    if interactive and not values.get("MIMO_API_KEY"):
        if not sys.stdin.isatty():
            raise ValueError("后台安装不能读取隐藏输入。请先填写本机 config.env，再使用 --non-interactive。")
        print("MiMo 密钥：打开 https://platform.xiaomimimo.com/ ，登录后进入控制台 > API Keys，创建并复制密钥。")
        values["MIMO_API_KEY"] = getpass.getpass("MiMo API Key：").strip()
    if interactive and yuanbao and not values.get("YUANBAO_COOKIE"):
        if not sys.stdin.isatty():
            raise ValueError("后台安装不能读取隐藏输入。请先在本机 config.env 填写 YUANBAO_COOKIE。")
        print("元宝 Cookie：登录 https://yuanbao.tencent.com/ ，右键 > 检查 > Network，点击 list 请求，在 Headers > Request Headers 中复制 Cookie 的完整值（不含 Cookie:）。")
        print("如果没有 list 请求，保持 Network 打开，给元宝发几句话，再查看新出现的 list 请求。")
        values["YUANBAO_COOKIE"] = getpass.getpass("腾讯元宝 Cookie：").strip()
    if not values.get("MIMO_API_KEY"):
        raise ValueError("缺少 MiMo API Key。请在本机配置文件中填写，或在交互终端运行安装脚本。")
    if yuanbao and not values.get("YUANBAO_COOKIE"):
        raise ValueError("视频号需要腾讯元宝 Cookie，请按 Skill 中的方法获取后填入本机配置。")
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description="安装本地视频转写工具")
    parser.add_argument("--install-dir", type=Path)
    parser.add_argument("--non-interactive", action="store_true")
    parser.add_argument("--with-yuanbao", action="store_true")
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        raise ValueError("需要 Python 3.10 或更新版本")
    state_path = SKILL_DIR / "installation.json"
    remembered = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    install_dir = (args.install_dir or Path(remembered.get("install_dir", DEFAULT_INSTALL_DIR))).expanduser().resolve()
    source = SKILL_DIR / "runtime"
    app_dir = install_dir / "app"
    if install_dir == SKILL_DIR or SKILL_DIR in install_dir.parents:
        raise ValueError("安装位置必须在 Skill 目录之外，避免把私人配置或运行环境混入发布文件")
    if not (source / "transcribe.py").is_file():
        raise ValueError("Skill 缺少 runtime 目录，请安装完整的 video-transcription 文件夹")
    if app_dir.exists() and not (app_dir / ".video-transcription-managed").exists():
        raise ValueError(f"安装目录已被其他文件占用，请换一个安装位置：{app_dir}")
    config_path = install_dir / "config.env"
    values = resolve_config(read_config(config_path), not args.non_interactive, args.with_yuanbao)
    write_config(config_path, values)
    shutil.copytree(source, app_dir, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (app_dir / ".video-transcription-managed").touch()
    python = app_dir / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.exists():
        subprocess.run([sys.executable, "-m", "venv", str(app_dir / ".venv")], check=True)
    subprocess.run([str(python), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(app_dir / "requirements.txt")], check=True)
    subprocess.run([str(python), "-c", "import sys, transcribe, subprocess; from pathlib import Path; transcribe.load_config(Path(sys.argv[1])); subprocess.run([transcribe.ffmpeg_path(), '-version'], check=True, stdout=subprocess.DEVNULL)", str(config_path)], cwd=app_dir, check=True)
    state_path.write_text(json.dumps({"install_dir": str(install_dir)}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"安装完成，音频工具已检查。配置保存在：{config_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"安装失败，子程序退出码：{exc.returncode}", file=sys.stderr)
        raise SystemExit(1)
    except Exception as exc:
        print(f"安装失败：{exc}", file=sys.stderr)
        raise SystemExit(1)
