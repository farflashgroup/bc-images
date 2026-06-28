import re
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "replace")

for slug, path in [
    ("eustaquio", "https://canadasoccer.com/profile/55651/stephen-eustaquio/"),
    ("larin", "https://canadasoccer.com/profile/3769/cyle-larin/"),
    ("johnston", "https://canadasoccer.com/profile/3772/alistair-johnston/"),
    ("davies", "https://canadasoccer.com/profile/5810/alphonso-davies/"),
]:
    try:
        html = fetch(path)
    except Exception as exc:
        print(slug, "fetch fail", exc)
        continue
    imgs = re.findall(r'https://[^"\']+\.(?:jpg|jpeg|png|webp)(?:\?[^"\']*)?', html, flags=re.I)
    imgs = [u for u in imgs if "og-jpg" not in u and "logo" not in u.lower()]
    print("\n===", slug, "===")
    for u in sorted(set(imgs))[:15]:
        print(u)

# roster search
try:
    html = fetch("https://canadasoccer.com/national-teams/mens/")
    imgs = re.findall(r'https://[^"\']+uploads[^"\']+\.(?:jpg|jpeg|png)', html, flags=re.I)
    print("\n=== mens roster uploads ===")
    for u in sorted(set(imgs))[:20]:
        print(u)
except Exception as exc:
    print("roster fail", exc)
