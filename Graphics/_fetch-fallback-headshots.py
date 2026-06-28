import re
import urllib.request
from PIL import Image
import io
from pathlib import Path

UA = "Mozilla/5.0"
ROOT = Path(__file__).resolve().parent / "article-assets" / "canmnt-squad" / "players"
BASE = "https://canadasoccer.com/wp-content/uploads/"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=45).read()


def save_png(slug, url):
    data = fetch(url)
    im = Image.open(io.BytesIO(data))
    dest = ROOT / f"{slug}.png"
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    im.save(dest, "PNG")
    print(f"saved {slug}: {im.size[0]}x{im.size[1]} {len(data)//1024}KB")


FALLBACKS = {
    "stephen-eustaquio": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Eustaquio_Stephen_Masked2024www.png",
    "jacob-shaffelburg": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Shaffelburg_Jacob_Masked2024www.png",
    "jayden-nelson": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Headshot/Nelson_Jayden2025www.jpg",
    "alfie-jones": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Headshot/Jones_Alfie2025www.jpg",
}

for slug, url in FALLBACKS.items():
    save_png(slug, url)

# Probe alternate Eustáquio profile
for pid in ["5005", "55651"]:
    html = fetch(f"https://canadasoccer.com/profile/{pid}/stephen-eustaquio/").decode("utf-8", "replace")
    paths = sorted(set(re.findall(r"canada-soccer-files/[^\"']+\.(?:jpg|png)", html, flags=re.I)))
    print(f"\nprofile {pid}:")
    for p in paths:
        if "TEAM_LOGO" in p:
            continue
        try:
            data = fetch(BASE + p.replace(" ", "%20"))
            im = Image.open(io.BytesIO(data))
            print(f"  {im.size} {len(data)//1024}KB {p}")
        except Exception as exc:
            print(f"  fail {p} {exc}")
