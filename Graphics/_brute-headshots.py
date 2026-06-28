import urllib.request
from PIL import Image
import io

UA = "Mozilla/5.0"
PREFIX = "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/"


def check(filename):
    url = PREFIX + filename
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        data = urllib.request.urlopen(req, timeout=20).read()
        im = Image.open(io.BytesIO(data))
        return im.size, len(data)
    except Exception:
        return None, None


players = {
    "Eustaquio": ["Eustaquio_Stephen_Masked2024www.png", "Eustaquio_Stephen_Masked2025www.png", "Eustaquio_Stephen_Masked2026www.png"],
    "Nelson": ["Nelson_Jayden_Masked2024www.png", "Nelson_Jayden_Masked2025www.png", "Nelson_Jayden_Masked2026www.png"],
    "Jones": ["Jones_Alfie_Masked2024www.png", "Jones_Alfie_Masked2025www.png", "Jones_Alfie_Masked2026www.png"],
    "Shaffelburg": ["Shaffelburg_Jacob_Masked2024www.png", "Shaffelburg_Jacob_Masked2025www.png", "Shaffelburg_Jacob_Masked2026www.png"],
    "Davies": ["Davies_Alphonso_Masked2024www.png", "Davies_Alphonso_Masked2025www.png", "Davies_Alphonso_Masked2026www.png"],
}

for player, files in players.items():
    print(f"\n{player}:")
    for f in files:
        size, nbytes = check(f)
        if size:
            print(f"  OK {f} -> {size[0]}x{size[1]} {nbytes//1024}KB")
        else:
            print(f"  -- {f}")

# Headshot folder variants
HEAD = "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Headshot/"
for f in [
    "Eustaquo_Stephen2024www.jpg",
    "Eustaquio_Stephen2026www.jpg",
    "Nelson_Jayden2026www.jpg",
    "Jones_Alfie2026www.jpg",
    "Shaffelburg_Jacob2026www.jpg",
    "Davies_Alphonso2026www.jpg",
]:
    url = HEAD + f
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        data = urllib.request.urlopen(req, timeout=20).read()
        im = Image.open(io.BytesIO(data))
        print(f"HEAD OK {f} -> {im.size} {len(data)//1024}KB")
    except Exception as exc:
        print(f"HEAD -- {f}")
