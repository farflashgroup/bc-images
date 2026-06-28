import re
import urllib.request
from pathlib import Path

UA = "Mozilla/5.0"
ROOT = Path(__file__).resolve().parent / "article-assets" / "canmnt-squad" / "players"

for slug, url in [
    ("jayden-nelson", "https://canadasoccer.com/profile/4274/jayden-nelson/"),
    ("alfie-jones", "https://canadasoccer.com/profile/57095/alfie-jones/"),
]:
    html = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=45).read().decode("utf-8", "replace")
    masked = re.findall(r"CANMNT-PNG/[^\"']+", html, flags=re.I)
    jpgs = re.findall(r"canada-soccer-files/[^\"']+\.(?:jpg|png)", html, flags=re.I)
    print(slug, url)
    for m in sorted(set(masked)):
        full = f"https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked profile photos/MNT/{m}".replace(" ", "%20")
        print(" ", full)
        try:
            data = urllib.request.urlopen(urllib.request.Request(full, headers={"User-Agent": UA}), timeout=30).read()
            (ROOT / f"{slug}.png").write_bytes(data)
            print("   saved", len(data))
        except Exception as exc:
            print("   fail", exc)
    for j in sorted(set(jpgs))[:5]:
        if "default" not in j and "og-" not in j:
            print("  jpg", j)
