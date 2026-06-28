import re
import urllib.request
from PIL import Image
import io

UA = "Mozilla/5.0"
BASE = "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked profile photos/MNT/CANMNT-PNG/"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=45).read()


html = fetch("https://canadasoccer.com/camp/1700/fifa-world-cup-2026/").decode("utf-8", "replace")
masked = sorted(set(re.findall(r"CANMNT-PNG/([^\"']+\.png)", html, flags=re.I)))

print(f"Found {len(masked)} masked PNGs on camp page\n")
for name in masked:
    url = BASE + name.replace(" ", "%20")
    try:
        data = fetch(url)
        im = Image.open(io.BytesIO(data))
        print(f"{im.size[0]:4}x{im.size[1]:4}  {len(data)//1024:4}KB  {name}")
    except Exception as exc:
        print(f"FAIL {name}: {exc}")
