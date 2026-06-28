import json
import urllib.parse
import urllib.request
from pathlib import Path
from PIL import Image

UA = "Mozilla/5.0"
ROOT = Path(__file__).resolve().parent / "article-assets" / "canmnt-squad" / "players"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=45).read()


def sportsdb(name):
    q = urllib.parse.quote(name)
    url = f"https://www.thesportsdb.com/api/v1/json/3/searchplayers.php?p={q}"
    data = json.loads(fetch(url).decode("utf-8"))
    for item in data.get("player") or []:
        if not item:
            continue
        return {
            "cutout": item.get("strCutout"),
            "thumb": item.get("strThumb"),
            "render": item.get("strRender"),
        }
    return {}


names = [
    "Stephen Eustáquio",
    "Cyle Larin",
    "Jayden Nelson",
    "Alfie Jones",
    "Jacob Shaffelburg",
]

for name in names:
    print(f"\n{name}:")
    info = sportsdb(name)
    for key, url in info.items():
        if not url:
            continue
        try:
            data = fetch(url)
            im = Image.open(__import__("io").BytesIO(data))
            print(f"  {key}: {im.size} {len(data)//1024}KB")
            print(f"    {url}")
        except Exception as exc:
            print(f"  {key} FAIL: {exc}")

print("\nLocal dimensions under 800px wide:")
for p in sorted(ROOT.glob("*.png")):
    im = Image.open(p)
    if im.size[0] < 800:
        print(f"  {p.name}: {im.size[0]}x{im.size[1]}")
