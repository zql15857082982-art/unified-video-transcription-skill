"""Copy only public runtime sources into the distributable skill."""
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
destination = root / "skills" / "video-transcription" / "runtime"
destination.mkdir(parents=True, exist_ok=True)
for name in ("transcribe.py", "report.py", "requirements.txt", "LICENSE", "THIRD_PARTY_NOTICES.md"):
    shutil.copy2(root / name, destination / name)
for file in (root / "app").rglob("*.py"):
    target = destination / file.relative_to(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(file, target)
for file in (root / "third_party").rglob("*"):
    if file.is_file() and file.name in {"LICENSE", "SOURCE.json", "ORIGINAL_NOTICES.md"}:
        target = destination / file.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, target)
print("已更新 Skill 内的公开运行文件，不含本机配置。")
