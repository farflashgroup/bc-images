"""Download and crop the Reuters logo from public sources."""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent / "article-assets"
UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def crop_logo(img: Image.Image, threshold: int = 250) -> Image.Image:
    rgba = img.convert("RGBA")
    w, h = rgba.size
    min_x, min_y, max_x, max_y = w, h, 0, 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = rgba.getpixel((x, y))
            if a < 16:
                continue
            if r >= threshold and g >= threshold and b >= threshold:
                continue
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
    if max_x <= min_x:
        return rgba
    return rgba.crop((min_x, min_y, max_x + 1, max_y + 1))


def commons_file_url(filename: str) -> str | None:
    title = urllib.parse.quote(filename.replace(" ", "_"))
    api = (
        "https://commons.wikimedia.org/w/api.php"
        f"?action=query&titles=File:{title}&prop=imageinfo&iiprop=url&format=json"
    )
    payload = json.loads(fetch(api).decode("utf-8"))
    pages = payload.get("query", {}).get("pages", {})
    for page in pages.values():
        info = page.get("imageinfo")
        if info:
            return info[0]["url"]
    return None


def scrape_reuters_logo_from_page() -> str | None:
    html = fetch(
        "https://ca.finance.yahoo.com/news/openai-defers-public-rollout-gpt-170216843.html"
    ).decode("utf-8", "replace")
    patterns = [
        r"https://[^\"']+reuters[^\"']+\.(?:svg|png)",
        r"https://[^\"']+Reuters[^\"']+\.(?:svg|png)",
    ]
    for pattern in patterns:
        for match in re.findall(pattern, html, flags=re.I):
            if "logo" in match.lower() or "brand" in match.lower():
                return match.replace("\\/", "/")
    return None


def save_png(source: bytes, dest: Path) -> None:
    img = Image.open(BytesIO(source))
    cropped = crop_logo(img)
    cropped.save(dest, optimize=True)
    print(f"Saved {dest} ({cropped.size[0]}x{cropped.size[1]})")


def main() -> None:
    svg_url = commons_file_url("Reuters logo.svg")
    if not svg_url:
        svg_url = "https://upload.wikimedia.org/wikipedia/commons/e/e2/Reuters_logo.svg"

    svg_dest = ROOT / "reuters-official.svg"
    svg_dest.write_bytes(fetch(svg_url))
    print(f"Saved {svg_dest} ({len(svg_dest.read_bytes())} bytes)")


if __name__ == "__main__":
    main()
