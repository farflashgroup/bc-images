import re
import urllib.request
from PIL import Image
import io

UA = "Mozilla/5.0"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=60).read()


html = fetch("https://canadasoccer.com/camp/1700/fifa-world-cup-2026/").decode("utf-8", "replace")

# all image-like URLs
patterns = [
    r"https://canadasoccer\.com/wp-content/uploads/[^\"'\s>]+\.(?:jpg|jpeg|png|webp)",
    r"canada-soccer-files/[^\"'\s>]+\.(?:jpg|jpeg|png|webp)",
]
found = set()
for pat in patterns:
    for m in re.findall(pat, html, flags=re.I):
        if m.startswith("http"):
            found.add(m)
        else:
            found.add("https://canadasoccer.com/wp-content/uploads/" + m.replace(" ", "%20"))

print(f"Total URLs: {len(found)}")
for url in sorted(found):
    if any(x in url.lower() for x in ["team_logo", "og-logo", "og-jpg", "default-"]):
        continue
    try:
        data = fetch(url)
        im = Image.open(io.BytesIO(data))
        if im.size[0] >= 400 or "masked" in url.lower() or "headshot" in url.lower():
            print(f"{im.size[0]:4}x{im.size[1]:4} {len(data)//1024:4}KB {url.split('/')[-1][:60]}")
    except Exception as exc:
        print(f"FAIL {url[-50:]} {exc}")
