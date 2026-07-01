"""Deep scrape for Reuters logo from Yahoo syndication and Reuters CDN."""
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
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch(url: str, headers: dict | None = None) -> bytes:
    h = dict(UA)
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
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


def rasterize_svg(svg_bytes: bytes, height: int = 160) -> Image.Image:
    try:
        import cairosvg  # type: ignore

        png = cairosvg.svg2png(bytestring=svg_bytes, output_height=height)
        return Image.open(BytesIO(png))
    except Exception as exc:
        raise RuntimeError(f"SVG rasterize failed: {exc}") from exc


def save_logo(raw: bytes, dest: Path, source: str) -> None:
    if raw[:100].lstrip().startswith(b"<"):
        img = rasterize_svg(raw)
    else:
        img = Image.open(BytesIO(raw))
    cropped = crop_logo(img)
    cropped.save(dest, optimize=True)
    (ROOT / "reuters-logo-source.json").write_text(
        json.dumps({"url": source, "size": list(cropped.size)}, indent=2),
        encoding="utf-8",
    )
    print(f"Saved {dest} ({cropped.size[0]}x{cropped.size[1]}) from {source}")


def yahoo_candidates() -> list[str]:
    html = fetch(
        "https://ca.finance.yahoo.com/news/openai-defers-public-rollout-gpt-170216843.html"
    ).decode("utf-8", "replace")

    urls = re.findall(r"https?://[^\"'\\]+", html)
    out: list[str] = []
    for url in urls:
        url = url.replace("\\u002F", "/").replace("\\/", "/")
        low = url.lower()
        if "yahoo" in low and "logo" in low:
            continue
        if "reuters" in low or ("logo" in low and "reuters" in html[max(0, html.find(url) - 200) : html.find(url) + 200].lower()):
            out.append(url)

    # JSON blobs often carry provider logo
    for blob in re.findall(r"\{[^{}]{0,4000}reuters[^{}]{0,4000}\}", html, flags=re.I):
        out.extend(re.findall(r"https?://[^\"'\\]+", blob))

    deduped: list[str] = []
    seen = set()
    for url in out:
        if url not in seen:
            seen.add(url)
            deduped.append(url)
    return deduped


def main() -> None:
    candidates = yahoo_candidates()
    print("Yahoo candidates:")
    for url in candidates:
        print(" ", url)

    candidates.extend(
        [
            "https://www.reuters.com/pf/resources/images/reuters-logo.svg?d=303",
            "https://www.reuters.com/pf/resources/images/reuters-logo.svg?d=152",
            "https://www.reuters.com/pf/resources/images/reuters-logo.png?d=152",
            "https://www.reuters.com/pf/resources/images/reuters-logo-v2.svg?d=303",
            "https://www.reuters.com/pf/resources/images/reuters-trust-logo.svg?d=152",
        ]
    )

    headers = {
        "Referer": "https://www.reuters.com/",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    }

    dest = ROOT / "reuters-logo-cropped.png"
    seen = set()
    for url in candidates:
        if url in seen:
            continue
        seen.add(url)
        try:
            raw = fetch(url, headers)
            if len(raw) < 120:
                continue
            if b"yahoo" in raw[:500].lower():
                print(f"Skip Yahoo asset: {url}")
                continue
            save_logo(raw, dest, url)
            return
        except Exception as exc:
            print(f"Failed {url}: {exc}")

    raise SystemExit("No Reuters logo found")


if __name__ == "__main__":
    main()
