"""Fetch company logos for Q2 2026 startup raises graphic."""
from __future__ import annotations

import json
import re
import ssl
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "article-assets" / "canada-startup-raises-q2-2026" / "logos"
MANIFEST = ROOT.parent / "logo-sources.json"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

COMPANIES = [
    {"slug": "cohere", "domain": "cohere.com"},
    {"slug": "nesto", "domain": "nesto.ca"},
    {"slug": "beacon", "domain": "beaconsoftware.com"},
    {"slug": "koho", "domain": "koho.ca"},
    {"slug": "float", "domain": "floatfinancial.com"},
    {"slug": "photonic", "domain": "photonic.com"},
    {"slug": "relay", "domain": "relayfi.com"},
    {"slug": "gaiia", "domain": "gaiia.com"},
    {"slug": "moment-energy", "domain": "momentenergy.com"},
    {"slug": "mecka-ai", "domain": "mecka.ai"},
    {"slug": "nord-quantique", "domain": "nordquantique.com"},
    {"slug": "saris", "domain": "saris.ai"},
    {"slug": "mappedin", "domain": "mappedin.com"},
    {"slug": "cleandesign", "domain": "cleandesign.ca"},
    {"slug": "tetrix", "domain": "tetrix.io"},
    {"slug": "celystra-pharma", "domain": "celystrapharma.com"},
    {"slug": "juno-industries", "domain": "junoindustries.com"},
    {"slug": "common-wealth", "domain": "commonwealthretirement.com"},
    {"slug": "lungpacer-medical", "domain": "lungpacer.com"},
    {"slug": "ns-tx-industries", "domain": "nstx.industries"},
    {"slug": "scispot", "domain": "scispot.com"},
    {"slug": "ak-robotics", "domain": "aandkrobotics.com"},
    {"slug": "pricepoint", "domain": "pricepoint.co"},
    {"slug": "gridbank", "domain": "gridbank.io"},
    {"slug": "flora", "domain": "heyflora.co"},
    {"slug": "viewsml", "domain": "viewsml.com"},
    {"slug": "sellit9", "domain": "sellit9.com"},
    {"slug": "sb-quantum", "domain": "sbquantum.com"},
    {"slug": "boostsecurity", "domain": "boostsecurity.io"},
    {"slug": "aux-labs", "domain": "auxlabs.ca"},
    {"slug": "aplantex", "domain": "aplantex.ca"},
    {"slug": "arcanus-aerial", "domain": "arcanus.ca"},
    {"slug": "coral", "domain": "coral.ca"},
    {"slug": "qubic", "domain": "qubictech.co"},
    {"slug": "june-health", "domain": "junehealth.co"},
    {"slug": "blossom-social", "domain": "blossomsocial.com"},
    {"slug": "databraid", "domain": "databraid.io"},
    {"slug": "zetane-systems", "domain": "zetane.com"},
    {"slug": "wygo", "domain": "wygo.com"},
    {"slug": "mystoria", "domain": "mystoria.com"},
    {"slug": "varvara-dev", "domain": "vardev.eu"},
    {"slug": "nomad", "domain": "nomad.io"},
    {"slug": "jetty", "domain": "jetty.io"},
    {"slug": "anchorbase", "domain": "anchorbase.com"},
    {"slug": "tydra-labs", "domain": "tydralabs.com"},
    {"slug": "carbonyx", "domain": "carbonyx.ca"},
    {"slug": "modern-mining-tech", "domain": "modernmining.com"},
    {"slug": "serenity-power", "domain": "serenitypower.ca"},
    {"slug": "savage-exploration", "domain": "savageexploration.ca"},
    {"slug": "tartan-app", "domain": "tartan.app"},
    {"slug": "sielo-robotics", "domain": "sielorobotics.com"},
    {"slug": "nightmare-games", "domain": "nightmare-games.com"},
    {"slug": "vitaliti-tech", "domain": "vitalititech.com"},
    {"slug": "courtstairs", "domain": "courtstairs.com"},
    {"slug": "fairly-staffing", "domain": "fairlystaffing.com"},
    {"slug": "timesmart-ai", "domain": "timesmart.ai"},
    {"slug": "foresight-spatial", "domain": "fslabs.ca"},
    {"slug": "sharkforce", "domain": "shark-force.com"},
    {"slug": "chemshift", "domain": "chemshift.com"},
    {"slug": "quadshift", "domain": "quadshift.io"},
    {"slug": "landing-zones", "domain": "landingzones.ca"},
    {"slug": "apera-ai", "domain": "apera.ai"},
    {"slug": "ecocero", "domain": "ecocero.com"},
]

# Hand-curated overrides for higher-quality logos
LOGO_OVERRIDES: dict[str, str] = {
    "ak-robotics": "https://images.squarespace-cdn.com/content/v1/6633dd53eeaf2f7ce1833a74/f9f3dc2f-c677-427d-9005-3673e55c44c5/%2BAK%2BRobotics%2BLogo%2B-%2BWhite.png?format=300w",
    "common-wealth": "https://www.commonwealthretirement.com/wp-content/uploads/2021/03/cropped-favicon-192x192.png",
    "pricepoint": "https://cdn.prod.website-files.com/68bff7d01af0d73fc257b761/68dabb0d0f65d7ee78cf8637_Group%2015.svg",
    "gridbank": "https://d375awjr36fy6n.cloudfront.net/static/marketplace/images/GridBank.io.png",
    "beacon": "https://beacon.inc/uploads/beacon-logo.png",
}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.og_image: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {k: (v or "") for k, v in attrs}
        if tag == "link":
            rel = attr.get("rel", "").lower()
            href = attr.get("href", "")
            if href and any(x in rel for x in ("icon", "apple-touch-icon", "shortcut")):
                self.links.append((rel, href))
        if tag == "meta" and attr.get("property") == "og:image":
            self.og_image = attr.get("content")


def fetch(url: str, timeout: int = 25) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read()


def abs_url(base: str, href: str) -> str:
    return urllib.parse.urljoin(base, href)


def image_ok(data: bytes) -> bool:
    if len(data) < 200:
        return False
    if data[:4] == b"\x89PNG" or data[:3] == b"\xff\xd8\xff":
        return True
    if data[:4] == b"RIFF" and b"WEBP" in data[:16]:
        return True
    if b"<svg" in data[:512].lower() or data.strip().startswith(b"<?xml"):
        return True
    if data[:4] in (b"GIF8", b"II*\x00", b"MM\x00*"):
        return True
    # ICO / favicon
    if data[:4] == b"\x00\x00\x01\x00":
        return True
    return len(data) >= 500


def ext_from_url(url: str, data: bytes) -> str:
    path = urllib.parse.urlparse(url).path.lower()
    for ext in (".png", ".jpg", ".jpeg", ".webp", ".svg", ".ico"):
        if path.endswith(ext):
            return ext.lstrip(".")
    if data[:4] == b"\x89PNG":
        return "png"
    if data[:3] == b"\xff\xd8\xff":
        return "jpg"
    if b"<svg" in data[:512].lower():
        return "svg"
    if data[:4] == b"\x00\x00\x01\x00":
        return "ico"
    return "png"


def scrape_site_icons(domain: str) -> list[str]:
    urls: list[str] = []
    for scheme in ("https", "http"):
        base = f"{scheme}://{domain}/"
        try:
            html = fetch(base).decode("utf-8", errors="replace")
            parser = LinkParser()
            parser.feed(html)
            if parser.og_image:
                urls.append(abs_url(base, parser.og_image))
            for _, href in parser.links:
                urls.append(abs_url(base, href))
            break
        except Exception:
            continue
    return urls


def candidate_urls(domain: str, slug: str) -> list[str]:
    urls: list[str] = []
    if slug in LOGO_OVERRIDES:
        urls.append(LOGO_OVERRIDES[slug])
    urls.extend(
        [
            f"https://logo.clearbit.com/{domain}",
            f"https://www.google.com/s2/favicons?domain={domain}&sz=256",
            f"https://icons.duckduckgo.com/ip3/{domain}.ico",
            f"https://{domain}/apple-touch-icon.png",
            f"https://{domain}/apple-touch-icon-precomposed.png",
            f"https://{domain}/favicon.ico",
            f"https://www.{domain}/favicon.ico" if not domain.startswith("www.") else "",
        ]
    )
    urls.extend(scrape_site_icons(domain))
    # de-dupe preserving order
    seen: set[str] = set()
    out: list[str] = []
    for u in urls:
        if not u or u in seen:
            continue
        seen.add(u)
        out.append(u)
    return out


def try_download(url: str) -> tuple[bytes, str] | None:
    try:
        data = fetch(url)
        if not image_ok(data):
            return None
        return data, ext_from_url(url, data)
    except Exception:
        return None


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, dict] = {}
    ok = 0
    fail: list[str] = []

    for company in COMPANIES:
        slug = company["slug"]
        domain = company["domain"]
        dest_base = ROOT / slug
        print(f"\n{slug} ({domain})")

        saved = False
        source_url = ""
        for url in candidate_urls(domain, slug):
            result = try_download(url)
            if not result:
                continue
            data, ext = result
            dest = dest_base.with_suffix(f".{ext}")
            dest.write_bytes(data)
            if slug in LOGO_OVERRIDES:
                (ROOT / f"{slug}-source.png").write_bytes(data)
            source_url = url
            print(f"  OK via {url} -> {dest.name} ({len(data)} bytes)")
            manifest[slug] = {"domain": domain, "source": url, "file": dest.name}
            ok += 1
            saved = True
            break

        if not saved:
            print("  FAIL - no logo found")
            fail.append(slug)
            manifest[slug] = {"domain": domain, "source": None, "file": None}

    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nDone: {ok}/{len(COMPANIES)} logos saved")
    if fail:
        print("Missing:", ", ".join(fail))


if __name__ == "__main__":
    main()
