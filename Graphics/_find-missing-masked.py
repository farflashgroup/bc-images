import re
import urllib.request

UA = "Mozilla/5.0"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "replace")

html = fetch("https://canadasoccer.com/profile/55651/stephen-eustaquio/")
for m in sorted(set(re.findall(r"CANMNT-PNG/[^\"']+", html, flags=re.I))):
    print(m)

for slug, guesses in {
    "eustaquio": [
        "Eustaquio_Stephen_Masked2026www.png",
        "Eust%C3%A1quio_Stephen_Masked2026www.png",
        "Eustaquio_Stephen_Masked2024www.png",
        "Eust%C3%A1quio_Stephen_Masked2024www.png",
    ],
    "nelson": ["Nelson_Jayden_Masked2026www.png", "Nelson_Jayden_Masked2024www.png"],
    "shaffelburg": ["Shaffelburg_Jacob_Masked2026www.png", "Shaffelburg_Jacob_Masked2024www.png"],
    "jones": ["Jones_Alfie_Masked2026www.png", "Jones_Alfie_Masked2024www.png"],
}.items():
    print(f"\n{slug}:")
    for g in guesses:
        url = f"https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/{g}"
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            data = urllib.request.urlopen(req, timeout=30).read()
            print(" OK", g, len(data))
        except Exception as exc:
            print(" NO", g, exc)
