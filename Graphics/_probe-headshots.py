import re
import urllib.request
from pathlib import Path
from PIL import Image
import io

UA = "Mozilla/5.0"
ROOT = Path(__file__).resolve().parent / "article-assets" / "canmnt-squad" / "players"

PROFILES = [
    ("stephen-eustaquio", "https://canadasoccer.com/profile/55651/stephen-eustaquio/"),
    ("jayden-nelson", "https://canadasoccer.com/profile/4274/jayden-nelson/"),
    ("alfie-jones", "https://canadasoccer.com/profile/57095/alfie-jones/"),
    ("jacob-shaffelburg", "https://canadasoccer.com/profile/3768/jacob-shaffelburg/"),
    ("cyle-larin", "https://canadasoccer.com/profile/3769/cyle-larin/"),
]

BASE = "https://canadasoccer.com/wp-content/uploads/"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=45).read()


def probe(slug, profile_url):
    html = fetch(profile_url).decode("utf-8", "replace")
    paths = sorted(
        set(
            re.findall(
                r"(?:canada-soccer-files/[^\"']+\.(?:jpg|jpeg|png|webp)|CANMNT-PNG/[^\"']+)",
                html,
                flags=re.I,
            )
        )
    )
    print(f"\n=== {slug} ===")
    for path in paths:
        if "TEAM_LOGO" in path or "default" in path or "og-" in path:
            continue
        url = BASE + path.replace(" ", "%20")
        try:
            data = fetch(url)
            im = Image.open(io.BytesIO(data))
            print(f"  {im.size[0]}x{im.size[1]}  {len(data)//1024}KB  {path}")
        except Exception as exc:
            print(f"  FAIL  {path}  {exc}")


for slug, url in PROFILES:
    probe(slug, url)
