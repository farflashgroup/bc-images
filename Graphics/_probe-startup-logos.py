"""Quick probe for startup logo URLs."""
import json
import ssl
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
ctx = ssl.create_default_context()

FIXES = {
    "cleandesign": ["cleandesign.ca", "https://www.cleandesign.ca/"],
    "ns-tx-industries": ["nstx.industries", "https://www.nstx.industries/"],
    "aux-labs": ["auxlabs.ca", "https://www.auxlabs.ca/"],
    "qubic": ["qubictech.co", "https://qubictech.co/"],
    "databraid": ["databraid.io", "https://www.databraid.io/"],
    "ak-robotics": ["aandkrobotics.com", "https://www.aandkrobotics.com/"],
}

OVERRIDES = {
    "ak-robotics": "https://images.squarespace-cdn.com/content/v1/6633dd53eeaf2f7ce1833a74/f9f3dc2f-c677-427d-9005-3673e55c44c5/%2BAK%2BRobotics%2BLogo%2B-%2BWhite.png?format=300w",
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
        return r.read()


def try_url(url):
    try:
        data = fetch(url)
        print(f"  OK {len(data)} {url[:90]}")
        return True
    except Exception as e:
        print(f"  -- {e} {url[:90]}")
        return False


for slug, (domain, home) in FIXES.items():
    print(f"\n{slug} -> {domain}")
    if slug in OVERRIDES:
        try_url(OVERRIDES[slug])
    for url in [
        f"https://logo.clearbit.com/{domain}",
        f"https://www.google.com/s2/favicons?domain={domain}&sz=256",
        f"https://icons.duckduckgo.com/ip3/{domain}.ico",
        f"https://{domain}/apple-touch-icon.png",
        f"https://{domain}/favicon.ico",
    ]:
        try_url(url)
