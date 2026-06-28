import re
import urllib.request
from pathlib import Path

UA = "Mozilla/5.0"
ROOT = Path(__file__).resolve().parent / "article-assets" / "canmnt-squad" / "players"

# Masked CANMNT PNG naming guesses + confirmed URLs from profile probes
MASKED = {
    "stephen-eustaquio": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Eustaquio_Stephen_Masked2024www.png",
    "cyle-larin": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Larin_Cyle_Masked2026www.png",
    "alistair-johnston": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Johnston_Alistair_Masked2026www.png",
    "alphonso-davies": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Davies_Alphonso_Masked2024www.png",
    "ismael-kone": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Kone_Ismael_Masked2026www.png",
    "promise-david": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/2025-CANMNT-PromiseDavid-4.png",
    "jonathan-david": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/David_Jonathan_Masked2026www.png",
    "maxime-crepeau": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Crepeau_Maxime_Masked2026www.png",
    "derek-cornelius": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Cornelius_Derek_Masked2026www.png",
    "jonathan-osorio": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Osorio_Jonathan_Masked2026www.png",
    "tajon-buchanan": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Buchanan_Tajon_Masked2026www.png",
    "moise-bombito": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Bombito_Moise_Masked2026www.png",
    "richie-laryea": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Laryea_Richie_Masked2026www.png",
    "liam-millar": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Millar_Liam_Masked2026www.png",
    "jayden-nelson": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Headshot/Nelson_Jayden2025www.jpg",
    "jacob-shaffelburg": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Shaffelburg_Jacob_Masked2024www.png",
    "dayne-st-clair": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/StClair_Dayne_Masked2026www.png",
    "joel-waterman": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Waterman_Joel_Masked2026www.png",
    "mathieu-choiniere": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Choiniere_Mathieu_Masked2026www.png",
    "nathan-saliba": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Saliba_Nathan_Masked2026www.png",
    "tani-oluwaseyi": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Oluwaseyi_Tani_Masked2026www.png",
    "owen-goodman": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Goodman_Owen_Masked2026www.png",
    "alfie-jones": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Headshot/Jones_Alfie2025www.jpg",
    "niko-sigur": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Sigur_Niko_Masked2026www.png",
    "luc-de-fougerolles": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/DeFougerolles_Luc_Masked2026www.png",
    "ali-ahmed": "https://canadasoccer.com/wp-content/uploads/canada-soccer-files/Masked%20profile%20photos/MNT/CANMNT-PNG/Ahmed_Ali_Masked2026www.png",
}

ALT_PATTERNS = [
    "St._Clair_Dayne_Masked2026www.png",
    "de_Fougerolles_Luc_Masked2026www.png",
    "De_Fougerolles_Luc_Masked2026www.png",
]


def try_download(url: str) -> tuple[int, bytes] | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        data = urllib.request.urlopen(req, timeout=45).read()
    except Exception:
        return None
    if len(data) < 8000 or data[:15].find(b"html") >= 0:
        return None
    return len(data), data


def main() -> None:
    ok = []
    miss = []
    for slug, url in MASKED.items():
        result = try_download(url)
        if result:
            size, data = result
            ext = ".png" if url.lower().endswith(".png") else ".jpg"
            dest = ROOT / f"{slug}{ext}"
            dest.write_bytes(data)
            # remove stale jpg if we saved png
            jpg = ROOT / f"{slug}.jpg"
            if ext == ".png" and jpg.exists():
                jpg.unlink()
            print(f"OK {slug}: {size} ({dest.name})")
            ok.append(slug)
            continue
        miss.append(slug)
        print(f"MISS {slug}")

    print(f"\n{len(ok)} ok, {len(miss)} miss")
    if miss:
        print(", ".join(miss))


if __name__ == "__main__":
    main()
