import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

SOURCE_DIR = BASE_DIR / "src"
TARGET_DIR = BASE_DIR / "src/static"

TARGET_DIR.mkdir(exist_ok=True)

for static_dir in SOURCE_DIR.rglob("static"):
    if static_dir == TARGET_DIR:
        continue

    for file in static_dir.rglob("*"):
        if file.is_file():
            dest = TARGET_DIR / file.name
            shutil.copy(file, dest)

print("Static files collected.")