"""Re-fetch and normalize selected startup logos for white card backgrounds."""
from __future__ import annotations

import shutil
import ssl
import urllib.request
from io import BytesIO
from pathlib import Path

import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parent / "article-assets" / "canada-startup-raises-q2-2026" / "logos"
OUT = ROOT / "normalized"
INK = (26, 26, 26)
GRIDBLUE = (47, 84, 235)
UA = {"User-Agent": "Mozilla/5.0"}
CTX = ssl.create_default_context()


def fetch(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers=UA)
    dest.write_bytes(urllib.request.urlopen(req, timeout=25, context=CTX).read())


def svg_to_png(svg_text: str, width: int) -> Image.Image:
    tmp = ROOT / "_tmp.svg"
    tmp.write_text(svg_text, encoding="utf-8")
    doc = fitz.open(str(tmp))
    page = doc[0]
    scale = width / page.rect.width
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=True)
    return Image.open(BytesIO(pix.tobytes("png"))).convert("RGBA")


def recolor_svg(path: Path, white_to: str = "#1A1A1A") -> str:
    svg = path.read_text(encoding="utf-8")
    svg = svg.replace('fill="#fff"', f'fill="{white_to}"')
    svg = svg.replace('fill="#FFF"', f'fill="{white_to}"')
    svg = svg.replace('fill="#ffffff"', f'fill="{white_to}"')
    svg = svg.replace('fill="white"', f'fill="{white_to}"')
    svg = svg.replace(".cls-2 {        fill: #fff;", f".cls-2 {{        fill: {white_to};")
    return svg


def strip_near_white(im: Image.Image, threshold: int = 248) -> Image.Image:
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 10 and min(r, g, b) >= threshold:
                px[x, y] = (r, g, b, 0)
    return im


def strip_color_backdrop(im: Image.Image, rgb: tuple[int, int, int], tol: int = 36) -> Image.Image:
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 10:
                continue
            if abs(r - rgb[0]) + abs(g - rgb[1]) + abs(b - rgb[2]) <= tol:
                px[x, y] = (r, g, b, 0)
    return im


def fit_logo(im: Image.Image, target: int = 80, wide_width: int = 128) -> Image.Image:
    im = im.convert("RGBA")
    bbox = im.getbbox()
    if not bbox:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    im = im.crop(bbox)
    w, h = im.size
    aspect = w / h
    if aspect >= 2.4:
        nw = wide_width
        nh = max(1, round(h * (wide_width / w)))
    else:
        scale = target / max(w, h)
        nw = max(1, round(w * scale))
        nh = max(1, round(h * scale))
    return im.resize((nw, nh), Image.Resampling.LANCZOS)


def save_slug(slug: str, im: Image.Image) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    out = fit_logo(im)
    out.save(OUT / f"{slug}.png", optimize=True)
    out.save(ROOT / f"{slug}.png", optimize=True)
    print(f"{slug}: {out.size}")


def fix_common_wealth() -> None:
    icon = ROOT / "common-wealth-icon.png"
    if not icon.is_file():
        fetch(
            "https://www.commonwealthretirement.com/wp-content/uploads/2021/03/cropped-favicon-192x192.png",
            icon,
        )
    im = Image.open(icon).convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 10 and max(r, g, b) < 28:
                px[x, y] = (r, g, b, 0)
    save_slug("common-wealth", im)


def fix_pricepoint() -> None:
    src = ROOT / "pricepoint-source.svg"
    if not src.is_file():
        fetch(
            "https://cdn.prod.website-files.com/68bff7d01af0d73fc257b761/68dabb0d0f65d7ee78cf8637_Group%2015.svg",
            src,
        )
    im = svg_to_png(recolor_svg(src), 1200)
    save_slug("pricepoint", im)


def fix_beacon() -> None:
    src = ROOT / "beacon-source.png"
    if not src.is_file():
        fetch("https://beacon.inc/uploads/beacon-logo.png", src)
    im = Image.open(src).convert("RGBA")
    im = im.resize((330, 330), Image.Resampling.LANCZOS)
    im = strip_near_white(strip_color_backdrop(im, (30, 58, 138), tol=48))
    save_slug("beacon", im)


def crop_gridbank_wordmark() -> Image.Image:
    og = ROOT / "gridbank-source.png"
    if not og.is_file():
        fetch(
            "https://d375awjr36fy6n.cloudfront.net/static/marketplace/images/GridBank.io.png",
            og,
        )
    im = Image.open(og).convert("RGBA")
    crop = im.crop((700, 455, 1220, 615))
    crop = strip_near_white(crop, threshold=252)
    bbox = crop.getbbox()
    if bbox:
        crop = crop.crop(bbox)
    px = crop.load()
    w, h = crop.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 10 and b > r + 20 and y > h * 0.72:
                px[x, y] = (r, g, b, 0)
    bbox = crop.getbbox()
    return crop.crop(bbox) if bbox else crop


def fix_gridbank() -> None:
    im = crop_gridbank_wordmark()
    save_slug("gridbank", im)


def main() -> None:
    fix_common_wealth()
    fix_pricepoint()
    fix_beacon()
    fix_gridbank()


if __name__ == "__main__":
    main()
