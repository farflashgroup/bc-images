import re
import urllib.request
from PIL import Image
import io

UA = "Mozilla/5.0"
BASE = "https://canadasoccer.com/wp-content/uploads/"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=45).read()


def check_url(url):
    try:
        data = fetch(url)
        im = Image.open(io.BytesIO(data))
        return im.size, len(data)
    except Exception as exc:
        return None, str(exc)


urls = [
    "https://canadasoccer.com/camp/1700/fifa-world-cup-2026/",
    "https://canadasoccer.com/teams/canada-men/",
]

for page in urls:
    html = fetch(page).decode("utf-8", "replace")
    paths = sorted(set(re.findall(r"canada-soccer-files/[^\"']+\.(?:jpg|jpeg|png|webp)", html, flags=re.I)))
    masked = sorted(set(re.findall(r"CANMNT-PNG/[^\"']+", html, flags=re.I)))
    print(f"\n=== {page} ===")
    for path in masked:
        if any(x in path.lower() for x in ["eustaquio", "jones", "nelson", "shaffelburg", "larin"]):
            url = BASE + "canada-soccer-files/Masked profile photos/MNT/" + path
            url = url.replace(" ", "%20")
            size, info = check_url(url)
            print(f"  {path} -> {size} {info}")

    for path in paths:
        if any(x in path.lower() for x in ["eustaquio", "jones_alfie", "nelson", "shaffelburg", "larin"]):
            url = BASE + path.replace(" ", "%20")
            size, info = check_url(url)
            print(f"  {path} -> {size} {info}")

# Brute-force common naming patterns
guesses = [
    "canada-soccer-files/Headshot/Eustaquio_Stephen2025www.jpg",
    "canada-soccer-files/Headshot/Eustaquio_Stephen2026www.jpg",
    "canada-soccer-files/Headshot/Jones_Alfie2025www.jpg",
    "canada-soccer-files/Headshot/Jones_Alfie2026www.jpg",
    "canada-soccer-files/Masked profile photos/MNT/CANMNT-PNG/Eustaquio_Stephen_Masked2026www.png",
    "canada-soccer-files/Masked profile photos/MNT/CANMNT-PNG/Jones_Alfie_Masked2026www.png",
    "canada-soccer-files/Masked profile photos/MNT/CANMNT-PNG/Nelson_Jayden_Masked2026www.png",
    "canada-soccer-files/Masked profile photos/MNT/Headshot/Nelson_Jayden2025www.jpg",
    "canada-soccer-files/Masked profile photos/MNT/Headshot/Jones_Alfie2025www.jpg",
]

print("\n=== URL guesses ===")
for path in guesses:
    url = BASE + path.replace(" ", "%20")
    size, info = check_url(url)
    if size:
        print(f"OK {path} -> {size} {info//1024}KB")
    else:
        print(f"NO {path}")
