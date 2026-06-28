import re
import urllib.request
from PIL import Image
import io

UA = "Mozilla/5.0"
BASE = "https://canadasoccer.com/wp-content/uploads/"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=45).read()


def check(path):
    url = BASE + path.replace(" ", "%20")
    try:
        data = fetch(url)
        im = Image.open(io.BytesIO(data))
        return im.size, len(data), url
    except Exception as exc:
        return None, None, str(exc)


html = fetch("https://canadasoccer.com/camp/1700/fifa-world-cup-2026/").decode("utf-8", "replace")
paths = sorted(set(re.findall(r"canada-soccer-files/[^\"']+\.(?:jpg|jpeg|png|webp)", html, flags=re.I)))
masked = sorted(set(re.findall(r"CANMNT-PNG/[^\"']+", html, flags=re.I)))

for path in paths + [f"canada-soccer-files/Masked profile photos/MNT/{m}" for m in masked]:
    if "TEAM_LOGO" in path or "default" in path:
        continue
    keys = ["eustaquio", "eust", "jones_alfie", "nelson", "shaffelburg", "larin"]
    if not any(k in path.lower() for k in keys):
        continue
    size, nbytes, info = check(path)
    if size:
        print(f"{size[0]}x{size[1]}  {nbytes//1024}KB  {path}")
    else:
        print(f"FAIL {path} {info}")

print("\nEustaquio guesses:")
for g in [
    "canada-soccer-files/Headshot/Eustaquio_Stephen2025www.jpg",
    "canada-soccer-files/Headshot/Eustaquio_Stephen2026www.jpg",
    "canada-soccer-files/Headshot/Eustáquio_Stephen2025www.jpg",
    "canada-soccer-files/Masked profile photos/MNT/CANMNT-PNG/Eustaquio_Stephen_Masked2024www.png",
    "canada-soccer-files/Masked profile photos/MNT/CANMNT-PNG/Eustaquio_Stephen_Masked2026www.png",
]:
    size, nbytes, info = check(g)
    print(g, "->", size, nbytes and nbytes // 1024, info if not size else "")
