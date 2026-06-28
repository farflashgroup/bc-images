import json
import urllib.parse
import urllib.request
from PIL import Image
import io

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=45).read()


def wiki_thumb(title):
    encoded = urllib.parse.quote(title.replace(" ", "_"), safe="")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    data = json.loads(fetch(url).decode("utf-8"))
    thumb = (data.get("thumbnail") or {}).get("source")
    if not thumb:
        return None
    # try original size
    orig = thumb.split("/thumb/")[0] + "/" + thumb.split("/")[-1].split("/")[0] if "/thumb/" in thumb else thumb
    return thumb, orig


players = [
    ("stephen-eustaquio", "Stephen_Eustáquio"),
    ("cyle-larin", "Cyle_Larin"),
    ("jayden-nelson", "Jayden_Nelson"),
    ("alfie-jones", "Alfie_Jones"),
    ("jacob-shaffelburg", "Jacob_Shaffelburg"),
]

for slug, wiki in players:
    print(f"\n{slug}:")
    try:
        thumb, orig = wiki_thumb(wiki)
        for label, url in [("thumb", thumb), ("orig", orig)]:
            if not url:
                continue
            try:
                data = fetch(url)
                im = Image.open(io.BytesIO(data))
                print(f"  {label}: {im.size[0]}x{im.size[1]} {len(data)//1024}KB")
                print(f"    {url[:100]}...")
            except Exception as exc:
                print(f"  {label} FAIL: {exc}")
    except Exception as exc:
        print(f"  wiki FAIL: {exc}")
