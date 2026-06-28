"""Normalize startup logos to equal visual size with transparent backgrounds."""
from __future__ import annotations

import shutil
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent / "article-assets" / "canada-startup-raises-q2-2026" / "logos"
RAW = ROOT / "_raw"
OUT = ROOT / "normalized"
CANVAS = 100
FILL = 0.8
TARGET = int(CANVAS * FILL)
INK = (26, 26, 26)

TETRIX_SOURCE = Path(
    r"C:\Users\lfara\.cursor\projects\c-Users-lfara-Desktop-Development-BC-Images\assets"
    r"\c__Users_lfara_AppData_Roaming_Cursor_User_workspaceStorage_20b2609507b014959a62490ae3e703f0_images_image-326bc6e7-6b88-45ea-9af2-957a0a86e17e.png"
)

EXT_MAP = {
    "beacon": "beacon-source.png",
    "koho": "koho.jpg",
    "juno-industries": "juno-industries.ico",
    "jetty": "jetty.ico",
    "carbonyx": "carbonyx.ico",
    "chemshift": "chemshift.ico",
    "databraid": "databraid.jpg",
    "varvara-dev": "varvara-dev.jpg",
    "serenity-power": "serenity-power.jpg",
}


def is_normalized_export(path: Path) -> bool:
    if path.suffix.lower() != ".png":
        return False
    try:
        with Image.open(path) as im:
            w, h = im.size
            return max(w, h) == TARGET
    except Exception:
        return False


def slug_files() -> dict[str, Path]:
    priority = {".jpg": 0, ".jpeg": 0, ".ico": 1, ".webp": 2, ".png": 3, ".svg": 4}
    slugs: set[str] = set()
    for path in ROOT.iterdir():
        if path.is_file() and path.suffix.lower() in priority and not path.name.startswith("_"):
            slugs.add(path.stem.replace("-source", ""))
    for slug in EXT_MAP:
        slugs.add(slug)

    mapping: dict[str, Path] = {}
    for slug in sorted(slugs):
        if slug.startswith("_"):
            continue
        candidates = list(ROOT.glob(f"{slug}.*"))
        if slug in EXT_MAP:
            override = ROOT / EXT_MAP[slug]
            if override.is_file():
                candidates.insert(0, override)
        source = ROOT / f"{slug}-source.png"
        if source.is_file():
            candidates.insert(0, source)
        candidates = [
            p for p in candidates if p.suffix.lower() in priority and (p.name.endswith("-source.png") or "-source" not in p.stem)
        ]
        if len(candidates) > 1:
            non_norm = [p for p in candidates if not is_normalized_export(p)]
            if non_norm:
                candidates = non_norm
        candidates.sort(key=lambda p: (priority.get(p.suffix.lower(), 9), -p.stat().st_size, p.name))
        if candidates:
            mapping[slug] = candidates[0]
    return mapping


def load_rgba(path: Path) -> Image.Image:
    if path.suffix.lower() == ".svg":
        try:
            import cairosvg  # type: ignore

            data = cairosvg.svg2png(url=str(path), output_width=512, output_height=512)
            return Image.open(BytesIO(data)).convert("RGBA")
        except Exception:
            raise ValueError("SVG requires cairosvg")
    im = Image.open(path)
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    return im


def opaque_pixels(im: Image.Image) -> list[tuple[int, int, int, int]]:
    im = im.convert("RGBA")
    return [im.getpixel((x, y)) for y in range(im.height) for x in range(im.width) if im.getpixel((x, y))[3] > 32]


def strip_pure_white_backdrop(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 10 and min(r, g, b) > 248:
                px[x, y] = (r, g, b, 0)
    return im


def apply_black_mask(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    _, _, _, alpha = im.split()
    px = opaque_pixels(im)
    if px:
        avg_a = sum(a for _, _, _, a in px) / len(px)
        max_a = max(a for _, _, _, a in px)
        if max_a < 200 or avg_a < 180:
            alpha = alpha.point(lambda a: 255 if a > 24 else 0)
    black = Image.new("RGBA", im.size, (*INK, 0))
    black.putalpha(alpha)
    return black


def corner_bg(im: Image.Image) -> tuple[int, int, int]:
    w, h = im.size
    points = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    rs, gs, bs = [], [], []
    for x, y in points:
        r, g, b, a = im.getpixel((x, y))
        if a > 10:
            rs.append(r)
            gs.append(g)
            bs.append(b)
    if not rs:
        return (255, 255, 255)
    return (sum(rs) // len(rs), sum(gs) // len(gs), sum(bs) // len(bs))


def is_white_logo(im: Image.Image) -> bool:
    px = opaque_pixels(im)
    if len(px) < 20:
        return False
    avg_lum = sum(0.299 * r + 0.587 * g + 0.114 * b for r, g, b, _ in px) / len(px)
    avg_chroma = sum(max(r, g, b) - min(r, g, b) for r, g, b, _ in px) / len(px)
    return avg_lum > 150 and avg_chroma < 25


def should_black_mask(im: Image.Image) -> bool:
    if is_white_logo(im):
        return True
    px = opaque_pixels(im)
    if len(px) < 20:
        return False
    alphas = [a for _, _, _, a in px]
    lums = [0.299 * r + 0.587 * g + 0.114 * b for r, g, b, _ in px]
    chroma = [max(r, g, b) - min(r, g, b) for r, g, b, _ in px]
    avg_a = sum(alphas) / len(alphas)
    max_a = max(alphas)
    avg_lum = sum(lums) / len(lums)
    avg_chroma = sum(chroma) / len(chroma)

    # Washed-out or nearly invisible alpha
    if max_a < 200 or avg_a < 160:
        return True
    # Faint grey monochrome marks (e.g. dark favicons scraped as mid-grey)
    if avg_chroma < 18 and 50 <= avg_lum <= 180:
        return True
    # Dark semi-transparent strokes
    if avg_lum < 80 and avg_a < 220 and avg_chroma < 40:
        return True
    return False


def prepare_logo(im: Image.Image) -> tuple[Image.Image, bool]:
    im = im.convert("RGBA")
    trial = remove_background(im.copy())
    if trial.getbbox() and len(opaque_pixels(trial)) >= 30:
        if should_black_mask(trial):
            return apply_black_mask(trial), True
        return trial, False
    stripped = strip_pure_white_backdrop(im)
    if should_black_mask(stripped):
        return apply_black_mask(stripped), True
    return trial if trial.getbbox() else im, False


def dist(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
    return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2) ** 0.5


def remove_background(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    w, h = im.size
    bg = corner_bg(im)
    px = im.load()
    threshold = 42

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 10:
                continue
            rgb = (r, g, b)
            if dist(rgb, bg) <= threshold:
                px[x, y] = (r, g, b, 0)
                continue
            if min(r, g, b) > 245:
                px[x, y] = (r, g, b, 0)
                continue
            if max(r, g, b) < 18:
                px[x, y] = (r, g, b, 0)

    return im


def normalize(im: Image.Image) -> tuple[Image.Image, bool]:
    im, masked = prepare_logo(im)
    bbox = im.getbbox()
    if not bbox:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0)), masked
    im = im.crop(bbox)
    w, h = im.size
    scale = TARGET / max(w, h)
    new_w = max(1, round(w * scale))
    new_h = max(1, round(h * scale))
    im = im.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)
    if masked:
        im = apply_black_mask(im)
    return im, masked


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    mapping = slug_files()

    if TETRIX_SOURCE.is_file():
        tetrix, _ = normalize(load_rgba(TETRIX_SOURCE))
        tetrix.save(OUT / "tetrix.png", optimize=True)
        print("tetrix: user reference")

    ok = 0
    masked_slugs: list[str] = []
    for slug, src in mapping.items():
        if slug == "tetrix" and (OUT / "tetrix.png").is_file():
            ok += 1
            continue
        try:
            im = load_rgba(src)
            out, masked = normalize(im)
            out.save(OUT / f"{slug}.png", optimize=True)
            if masked:
                masked_slugs.append(slug)
            tag = " (black mask)" if masked else ""
            print(f"{slug}: {src.name} -> normalized{tag}")
            ok += 1
        except Exception as exc:  # noqa: BLE001
            print(f"{slug}: FAIL {exc}")

    # Replace root logos with normalized copies for HTML paths
    for path in OUT.glob("*.png"):
        dest = ROOT / path.name
        shutil.copy2(path, dest)

    manifest = ROOT.parent / "masked-logos.json"
    manifest.write_text(__import__("json").dumps(sorted(set(masked_slugs)), indent=2), encoding="utf-8")

    print(f"\nDone: {ok}/{len(mapping)} logos normalized to {TARGET}px max dimension @ {int(FILL * 100)}% fill")
    if masked_slugs:
        print(f"Black-masked logos: {', '.join(sorted(set(masked_slugs)))}")


if __name__ == "__main__":
    main()
