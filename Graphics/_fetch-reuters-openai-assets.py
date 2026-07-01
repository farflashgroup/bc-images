"""Fetch Reuters OpenAI GPT-5.6 article hero and logo assets."""
from __future__ import annotations

import re
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent / "article-assets"
ROOT.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BuildCanada/1.0"}


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


def save_logo(source_url: str, dest: Path) -> None:
    raw = fetch(source_url)
    img = Image.open(BytesIO(raw))
    cropped = crop_logo(img)
    cropped.save(dest, optimize=True)
    print(f"Saved logo {dest} ({cropped.size[0]}x{cropped.size[1]})")


def try_article_hero(url: str) -> str | None:
    html = fetch(url).decode("utf-8", "replace")
    for pattern in (
        r'property="og:image" content="([^"]+)"',
        r'name="twitter:image" content="([^"]+)"',
        r'"thumbnailUrl"\s*:\s*"([^"]+)"',
    ):
        match = re.search(pattern, html)
        if match:
            return match.group(1).replace("&amp;", "&")
    return None


def main() -> None:
    hero_candidates = []
    for article_url in (
        "https://ca.finance.yahoo.com/news/openai-defers-public-rollout-gpt-170216843.html",
        "https://www.reuters.com/legal/litigation/openai-defers-public-rollout-gpt56-us-seeks-early-access-frontier-ai-models-2026-06-26/",
    ):
        try:
            found = try_article_hero(article_url)
            if found:
                hero_candidates.append(found)
        except Exception as exc:
            print(f"Article hero fetch failed ({article_url}): {exc}")

    hero_candidates.append(
        "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=1600&q=80"
    )

    hero_url = next((u for u in hero_candidates if u), None)
    if not hero_url:
        raise SystemExit("No hero image found")

    print(f"Hero source: {hero_url}")
    hero_bytes = fetch(hero_url)
    hero_path = ROOT / "reuters-openai-gpt56-hero.jpg"
    img = Image.open(BytesIO(hero_bytes)).convert("RGB")
    # Target ~1600px wide for hero band
    if img.width > 1800:
        ratio = 1600 / img.width
        img = img.resize((1600, max(1, int(img.height * ratio))), Image.Resampling.LANCZOS)
    img.save(hero_path, "JPEG", quality=88, optimize=True)
    print(f"Saved hero {hero_path} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
