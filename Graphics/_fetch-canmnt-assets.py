"""Download CANMNT player portraits and club logos for squad profile cards."""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "article-assets" / "canmnt-squad"
PLAYERS_DIR = ROOT / "players"
CLUBS_DIR = ROOT / "clubs"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

PLAYERS = [
    {"slug": "ali-ahmed", "wiki": "Ali_Ahmed_(soccer)", "club": "norwich-city", "clubSearch": "Norwich City"},
    {"slug": "moise-bombito", "wiki": "Moïse_Bombito", "club": "nice", "clubSearch": "OGC Nice"},
    {"slug": "tajon-buchanan", "wiki": "Tajon_Buchanan", "club": "villarreal", "clubSearch": "Villarreal"},
    {"slug": "mathieu-choiniere", "wiki": "Mathieu_Choinière", "club": "lafc", "clubSearch": "Los Angeles FC"},
    {"slug": "derek-cornelius", "wiki": "Derek_Cornelius", "club": "rangers", "clubSearch": "Rangers"},
    {"slug": "maxime-crepeau", "wiki": "Maxime_Crépeau", "club": "orlando-city", "clubSearch": "Orlando City"},
    {"slug": "alphonso-davies", "wiki": "Alphonso_Davies", "club": "bayern-munich", "clubSearch": "Bayern Munich"},
    {"slug": "jonathan-david", "wiki": "Jonathan_David", "club": "juventus", "clubSearch": "Juventus"},
    {"slug": "promise-david", "wiki": "Promise_David", "club": "union-sg", "clubSearch": "Union Saint-Gilloise"},
    {"slug": "luc-de-fougerolles", "wiki": "Luc_de_Fougerolles", "club": "dender", "clubSearch": "Dender"},
    {"slug": "stephen-eustaquio", "wiki": "Stephen_Eustáquio", "club": "lafc", "clubSearch": "Los Angeles FC"},
    {"slug": "owen-goodman", "wiki": "Owen_Goodman", "club": "barnsley", "clubSearch": "Barnsley"},
    {"slug": "alistair-johnston", "wiki": "Alistair_Johnston", "club": "celtic", "clubSearch": "Celtic"},
    {"slug": "alfie-jones", "wiki": "Alfie_Jones", "club": "middlesbrough", "clubSearch": "Middlesbrough"},
    {"slug": "ismael-kone", "wiki": "Ismaël_Koné", "club": "sassuolo", "clubSearch": "Sassuolo"},
    {"slug": "cyle-larin", "wiki": "Cyle_Larin", "club": "southampton", "clubSearch": "Southampton"},
    {"slug": "richie-laryea", "wiki": "Richie_Laryea", "club": "toronto-fc", "clubSearch": "Toronto FC"},
    {"slug": "liam-millar", "wiki": "Liam_Millar", "club": "hull-city", "clubSearch": "Hull City"},
    {"slug": "jayden-nelson", "wiki": "Jayden_Nelson", "club": "austin-fc", "clubSearch": "Austin FC"},
    {"slug": "tani-oluwaseyi", "wiki": "Tani_Oluwaseyi", "club": "villarreal", "clubSearch": "Villarreal"},
    {"slug": "jonathan-osorio", "wiki": "Jonathan_Osorio", "club": "toronto-fc", "clubSearch": "Toronto FC"},
    {"slug": "nathan-saliba", "wiki": "Nathan_Saliba", "club": "anderlecht", "clubSearch": "Anderlecht"},
    {"slug": "jacob-shaffelburg", "wiki": "Jacob_Shaffelburg", "club": "lafc", "clubSearch": "Los Angeles FC"},
    {"slug": "niko-sigur", "wiki": "Niko_Sigur", "club": "hajduk-split", "clubSearch": "Hajduk Split"},
    {"slug": "dayne-st-clair", "wiki": "Dayne_St._Clair", "club": "inter-miami", "clubSearch": "Inter Miami"},
    {"slug": "joel-waterman", "wiki": "Joel_Waterman", "club": "chicago-fire", "clubSearch": "Chicago Fire"},
]


def fetch(url: str, timeout: int = 45) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def download(url: str, dest: Path) -> bool:
    try:
        data = fetch(url)
        if len(data) < 400:
            raise ValueError("response too small")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        print(f"  saved {dest.name} ({len(data)} bytes)")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"  FAIL {dest.name}: {exc}")
        return False


def wiki_summary_photo(title: str) -> str | None:
    encoded = urllib.parse.quote(title.replace(" ", "_"), safe="")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    try:
        data = json.loads(fetch(url).decode("utf-8"))
    except Exception:
        return None
    thumb = data.get("thumbnail") or {}
    return thumb.get("source")


def sportsdb_team_badge(team_name: str) -> str | None:
    q = urllib.parse.quote(team_name)
    url = f"https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={q}"
    try:
        data = json.loads(fetch(url).decode("utf-8"))
        teams = data.get("teams") or []
        if not teams:
            return None
        return teams[0].get("strBadge")
    except Exception:
        return None


def sportsdb_player_photo(player_name: str) -> str | None:
    q = urllib.parse.quote(player_name)
    url = f"https://www.thesportsdb.com/api/v1/json/3/searchplayers.php?p={q}"
    try:
        data = json.loads(fetch(url).decode("utf-8"))
        players = data.get("player") or []
        for item in players:
            if not item:
                continue
            cutout = item.get("strCutout") or item.get("strThumb")
            if cutout:
                return cutout
        return None
    except Exception:
        return None


def display_name(slug: str) -> str:
    return slug.replace("-", " ").title().replace("Moise", "Moïse").replace("Choiniere", "Choinière").replace("Crepeau", "Crépeau").replace("Eustaquio", "Eustáquio").replace("Ismael", "Ismaël").replace("De Fougerolles", "de Fougerolles")


def main() -> None:
    PLAYERS_DIR.mkdir(parents=True, exist_ok=True)
    CLUBS_DIR.mkdir(parents=True, exist_ok=True)

    club_cache: dict[str, str | None] = {}

    print("Club logos")
    for player in PLAYERS:
        slug = player["club"]
        if slug in club_cache:
            continue
        dest = CLUBS_DIR / f"{slug}.png"
        if dest.exists() and dest.stat().st_size > 2000:
            print(f"  skip {slug}")
            club_cache[slug] = str(dest)
            continue
        badge = sportsdb_team_badge(player["clubSearch"])
        club_cache[slug] = badge
        if badge:
            download(badge, dest)
        else:
            print(f"  no badge for {slug}")
        time.sleep(0.35)

    print("\nPlayer portraits")
    missing: list[str] = []
    for player in PLAYERS:
        slug = player["slug"]
        dest = PLAYERS_DIR / f"{slug}.jpg"
        if dest.exists() and dest.stat().st_size > 5000:
            print(f"  skip {slug}")
            continue

        photo_url = wiki_summary_photo(player["wiki"])
        if photo_url and download(photo_url, dest):
            time.sleep(0.35)
            continue

        fallback = sportsdb_player_photo(display_name(slug))
        if fallback and download(fallback, dest):
            time.sleep(0.35)
            continue

        print(f"  no photo for {slug}")
        missing.append(slug)
        time.sleep(0.35)

    if missing:
        print("\nMissing portraits:", ", ".join(missing))
    else:
        print("\nAll portraits downloaded.")


if __name__ == "__main__":
    main()
