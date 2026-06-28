"""Detect all-white logos and recolour them to brand ink using the alpha channel."""
from __future__ import annotations

import json
import ssl
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent / "article-assets" / "canada-startup-raises-q2-2026" / "logos"
MANIFEST = ROOT.parent / "masked-logos.json"
INK = (26, 26, 26)

AK_SOURCE = (
    "https://images.squarespace-cdn.com/content/v1/6633dd53eeaf2f7ce1833a74/"
    "f9f3dc2f-c677-427d-9005-3673e55c44c5/%2BAK%2BRobotics%2BLogo%2B-%2BWhite.png?format=300w"
)


def opaque_pixels(im: Image.Image) -> list[tuple[int, int, int, int]]:
    im = im.convert("RGBA")
    return [im.getpixel((x, y)) for y in range(im.height) for x in range(im.width) if im.getpixel((x, y))[3] > 32]


def is_white_logo(im: Image.Image) -> bool:
    px = opaque_pixels(im)
    if len(px) < 20:
        return False

    lums = [0.299 * r + 0.587 * g + 0.114 * b for r, g, b, _ in px]
    chroma = [max(r, g, b) - min(r, g, b) for r, g, b, _ in px]
    avg_lum = sum(lums) / len(lums)
    avg_chroma = sum(chroma) / len(chroma)
    dark = sum(1 for l in lums if l < 90) / len(px)
    very_light = sum(1 for r, g, b, _ in px if min(r, g, b) > 215) / len(px)
    near_white = sum(
        1 for r, g, b, _ in px if min(r, g, b) > 200 and max(r, g, b) - min(r, g, b) < 30
    ) / len(px)

    if near_white > 0.72 and avg_chroma < 28:
        return True
    if very_light > 0.82 and avg_chroma < 22:
        return True
    if avg_lum > 190 and avg_chroma < 18 and dark < 0.05:
        return True
    return False


def should_black_mask(im: Image.Image) -> bool:
    import importlib.util

    spec = importlib.util.spec_from_file_location("norm", Path(__file__).parent / "_normalize-startup-logos.py")
    norm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(norm)
    return norm.should_black_mask(im)


def apply_black_mask(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    _, _, _, alpha = im.split()
    black = Image.new("RGBA", im.size, (*INK, 0))
    black.putalpha(alpha)
    return black


def refresh_ak_robotics() -> None:
    req = urllib.request.Request(AK_SOURCE, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, context=ssl.create_default_context()).read()
    (ROOT / "ak-robotics-source.png").write_bytes(data)


def main() -> None:
    if not (ROOT / "ak-robotics-source.png").exists() or (ROOT / "ak-robotics.png").stat().st_size < 2000:
        try:
            refresh_ak_robotics()
            src = Image.open(ROOT / "ak-robotics-source.png").convert("RGBA")
            # Re-normalize quickly via import
            import importlib.util

            spec = importlib.util.spec_from_file_location("norm", Path(__file__).parent / "_normalize-startup-logos.py")
            norm = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(norm)
            src = norm.normalize(src)
            src.save(ROOT / "ak-robotics.png")
            print("ak-robotics: restored from source")
        except Exception as exc:  # noqa: BLE001
            print(f"ak-robotics: restore failed ({exc})")

    masked: list[str] = []
    for path in sorted(ROOT.glob("*.png")):
        if path.name.startswith("_") or path.name.endswith("-source.png"):
            continue
        im = Image.open(path)
        if not should_black_mask(im):
            continue
        out = apply_black_mask(im)
        out.save(path, optimize=True)
        masked.append(path.stem)
        print(f"masked: {path.stem}")

    MANIFEST.write_text(json.dumps(masked, indent=2), encoding="utf-8")
    print(f"\nDone: {len(masked)} logos black-masked -> {MANIFEST.name}")


if __name__ == "__main__":
    main()
