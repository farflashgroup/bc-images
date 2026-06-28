import json
import re
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

PROFILES = [
    ("stephen-eustaquio", "https://canadasoccer.com/profile/55651/stephen-eustaquio/"),
    ("cyle-larin", "https://canadasoccer.com/profile/3768/cyle-larin/"),
    ("alistair-johnston", "https://canadasoccer.com/profile/3772/alistair-johnston/"),
    ("alphonso-davies", "https://canadasoccer.com/profile/5810/alphonso-davies/"),
    ("jonathan-david", "https://canadasoccer.com/profile/3767/jonathan-david/"),
    ("maxime-crepeau", "https://canadasoccer.com/profile/3770/maxime-crepeau/"),
    ("derek-cornelius", "https://canadasoccer.com/profile/3771/derek-cornelius/"),
    ("jonathan-osorio", "https://canadasoccer.com/profile/3768/jonathan-osorio/"),
    ("tajon-buchanan", "https://canadasoccer.com/profile/55654/tajon-buchanan/"),
    ("moise-bombito", "https://canadasoccer.com/profile/55655/moise-bombito/"),
    ("ismael-kone", "https://canadasoccer.com/profile/55656/ismael-kone/"),
    ("richie-laryea", "https://canadasoccer.com/profile/55650/richie-laryea/"),
    ("liam-millar", "https://canadasoccer.com/profile/55649/liam-millar/"),
    ("jayden-nelson", "https://canadasoccer.com/profile/55648/jayden-nelson/"),
    ("jacob-shaffelburg", "https://canadasoccer.com/profile/55645/jacob-shaffelburg/"),
    ("dayne-st-clair", "https://canadasoccer.com/profile/55644/dayne-st-clair/"),
    ("joel-waterman", "https://canadasoccer.com/profile/55643/joel-waterman/"),
    ("mathieu-choiniere", "https://canadasoccer.com/profile/55653/mathieu-choiniere/"),
    ("nathan-saliba", "https://canadasoccer.com/profile/55646/nathan-saliba/"),
    ("tani-oluwaseyi", "https://canadasoccer.com/profile/55647/tani-oluwaseyi/"),
    ("promise-david", "https://canadasoccer.com/profile/57098/promise-david/"),
    ("owen-goodman", "https://canadasoccer.com/profile/57096/owen-goodman/"),
    ("alfie-jones", "https://canadasoccer.com/profile/57095/alfie-jones/"),
    ("niko-sigur", "https://canadasoccer.com/profile/57094/niko-sigur/"),
    ("luc-de-fougerolles", "https://canadasoccer.com/profile/57097/luc-de-fougerolles/"),
    ("ali-ahmed", "https://canadasoccer.com/profile/57100/ali-ahmed/"),
]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "replace")


def pick(html: str) -> list[str]:
    out = []
    out.extend(
        re.findall(
            r"https://canadasoccer\.com/wp-content/uploads/canada-soccer-files/Masked profile photos/MNT/CANMNT-PNG/[^\"']+",
            html,
            flags=re.I,
        )
    )
    out.extend(
        re.findall(
            r"https://canadasoccer\.com/wp-content/uploads/canada-soccer-files/[^\"']+\.(?:jpg|jpeg|png|webp)",
            html,
            flags=re.I,
        )
    )
    out.extend(re.findall(r"https://cdn\.scoreplay\.io/[^\"']+_compressed\.jpg", html, flags=re.I))
    cleaned = []
    for url in out:
        low = url.lower()
        if any(x in low for x in ("default-male", "og-jpg", "og-logo", "banner", "team_logo", "favicon", "apple-touch")):
            continue
        cleaned.append(url.replace(" ", "%20"))
    return cleaned


for slug, url in PROFILES:
    try:
        html = fetch(url)
        title = re.search(r"<h1[^>]*>([^<]+)</h1>", html)
        photos = pick(html)
        print(slug, "->", title.group(1).strip() if title else "?")
        for p in photos[:3]:
            print("  ", p)
    except Exception as exc:
        print(slug, "FAIL", exc)
