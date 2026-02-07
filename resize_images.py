"""Resize images from data/images/ into static/images/ as webp for web deployment."""

from pathlib import Path
from PIL import Image

SRC = Path("data/images")
DST = Path("static/images")
MAX_SIZE = 1400
QUALITY = 75

DST.mkdir(parents=True, exist_ok=True)

images = list(SRC.glob("*.jpg"))
total = len(images)

for i, src_path in enumerate(images, 1):
    dst_path = DST / (src_path.stem + ".webp")
    try:
        with Image.open(src_path) as img:
            img.thumbnail((MAX_SIZE, MAX_SIZE), Image.LANCZOS)
            img.save(dst_path, "WEBP", quality=QUALITY)
        print(f"[{i}/{total}] {src_path.name}")
    except Exception as e:
        print(f"[{i}/{total}] FAILED {src_path.name}: {e}")

print(f"\nDone. Resized {total} images to {DST}/")
