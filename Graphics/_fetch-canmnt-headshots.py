import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
ROOT = Path(__file__).resolve().parent / "article-assets" / "canmnt-squad" / "players"

NAMES = [
    "Ali Ahmed", "Moïse Bombito", "Tajon Buchanan", "Mathieu Choinière", "Derek Cornelius",
    "Maxime Crépeau", "Alphonso Davies", "Jonathan David", "Promise David", "Luc de Fougerolles",
    "Stephen Eustáquio", "Owen Goodman", "Alistair Johnston", "Alfie Jones", "Ismaël Koné",
    "Cyle Larin", "Richie Laryea", "Liam Millar", "Jayden Nelson", "Tani Oluwaseyi",
    "Jonathan Osorio", "Nathan Saliba", "Jacob Shaffelburg", "Niko Sigur", "Dayne St. Clair",
    "Joel Waterman",
]


def slugify(name: str) -> str:
    import unicodedata

    text = "".join(c for c in unicodedata.normalize("NFD", name) if unicodedata.category(c) != "Mn")
    return re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", text.lower()))


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "replace")


def download(url: str, dest: Path) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    data = urllib.request.urlopen(req, timeout=45).read()
    dest.write_bytes(data)
    return len(data)


def find_profile_url(name: str) -> str | None:
    q = urllib.parse.quote(name)
    search_url = f"https://canadasoccer.com/?s={q}"
    html = fetch(search_url)
    # profile links like /profile/3772/alistair-johnston/
    links = re.findall(r'href="(https://canadasoccer\.com/profile/\d+/[^"/]+/?)"', html, flags=re.I)
    slug = slugify(name).replace("moise", "moise").replace("eustaquio", "eustaquio")
    for link in links:
        if slug.replace("-", "") in link.replace("-", "").lower():
            return link
    return links[0] if links else None


def pick_photo(html: str) -> str | None:
    masked = re.findall(
        r'(https://canadasoccer\.com/wp-content/uploads/canada-soccer-files/Masked profile photos/MNT/CANMNT-PNG/[^"\']+)',
        html,
        flags=re.I,
    )
    if masked:
        return masked[0].replace(" ", "%20")

    files = re.findall(
        r'(https://canadasoccer\.com/wp-content/uploads/canada-soccer-files/[^"\']+\.(?:jpg|jpeg|png|webp))',
        html,
        flags=re.I,
    )
    for url in files:
        low = url.lower()
        if any(x in low for x in ("default-male", "og-jpg", "og-logo", "banner", "team_logo")):
            continue
        return url

    scoreplay = re.findall(
        r'(https://cdn\.scoreplay\.io/[^"\']+_compressed\.jpg)',
        html,
        flags=re.I,
    )
    if scoreplay:
        return scoreplay[0]

    return None


def main() -> None:
    results = {}
    for name in NAMES:
        slug = slugify(name)
        dest = ROOT / f"{slug}.jpg"
        try:
            profile = find_profile_url(name)
            if not profile:
                print(f"{slug}: no profile")
                continue
            html = fetch(profile)
            photo = pick_photo(html)
            if not photo:
                print(f"{slug}: no photo on {profile}")
                continue
            size = download(photo, dest)
            results[slug] = {"profile": profile, "photo": photo, "bytes": size}
            print(f"{slug}: {size} bytes from {photo.split('/')[-1]}")
        except Exception as exc:  # noqa: BLE001
            print(f"{slug}: FAIL {exc}")
        time.sleep(0.5)

    (ROOT.parent / "headshot-sources.json").write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
