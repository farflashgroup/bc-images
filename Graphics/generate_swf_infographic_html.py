import csv
import html
import math
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = Path(r"d:\Downloads\sovereign_wealth_funds_2026_final.csv")
OUTPUT_PATH = ROOT / "Graphics" / "sovereign-wealth-funds-2026.html"

WIDTH = 1080
HEIGHT = 1350

ALIASES = {
    "Bosnia & Herzegovina": "Bosnia and Herzegovina",
    "Cabo Verde": "Cape Verde",
    "Congo (Dem. Rep.)": "Democratic Republic of the Congo",
    "Congo (Rep.)": "Republic of the Congo",
    "Côte d'Ivoire": "Ivory Coast",
    "DR Congo": "Democratic Republic of the Congo",
    "Eswatini": "Swaziland",
    "Gambia": "The Gambia",
    "North Macedonia": "Macedonia",
    "Palestine": "West Bank",
    "São Tomé & Príncipe": "Sao Tome and Principe",
    "South Sudan": "S. Sudan",
    "Tanzania": "United Republic of Tanzania",
    "Trinidad & Tobago": "Trinidad and Tobago",
    "Türkiye": "Turkey",
    "United Kingdom": "England",
    "United States": "USA",
}

LEADERS = [
    ("NO", "Government Pension Fund Global", "$1.75T USD - NVIDIA, TSMC, TESLA, AMAZON", "$318K USD PER CAPITA"),
    ("CN", "China Investment Corporation", "$1.35T USD - BLACKSTONE, MORGAN STANLEY", "$960 USD PER CAPITA"),
    ("AE", "Abu Dhabi Investment Authority", "$1.1T USD - CITI, UBER, MANCITY, RELIANCE RETAIL", "$110K USD PER CAPITA"),
    ("KW", "Kuwait Investment Authority", "$900B USD - BP, VOLKSWAGEN, CITIGROUP", "$184K USD PER CAPITA"),
    ("SA", "Public Investment Fund", "$750B USD - LUCID MOTORS, BOEING, EA", "$20K USD PER CAPITA"),
]


def load_statuses():
    statuses = {}
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            country = row["Country"].strip()
            statuses[ALIASES.get(country, country)] = {
                "status": row["SWF?"].strip(),
                "funding_type": row["Funding Type"].strip(),
            }
    return statuses


def robinson(lon, lat):
    x_table = [
        1.0000, 0.9986, 0.9954, 0.9900, 0.9822, 0.9730, 0.9600,
        0.9427, 0.9216, 0.8962, 0.8679, 0.8350, 0.7986, 0.7597,
        0.7186, 0.6732, 0.6213, 0.5722, 0.5322,
    ]
    y_table = [
        0.0000, 0.0620, 0.1240, 0.1860, 0.2480, 0.3100, 0.3720,
        0.4340, 0.4958, 0.5571, 0.6176, 0.6769, 0.7346, 0.7903,
        0.8435, 0.8936, 0.9394, 0.9761, 1.0000,
    ]
    sign = -1 if lat < 0 else 1
    lat_abs = min(abs(lat), 90)
    idx = min(int(lat_abs // 5), 17)
    frac = (lat_abs - idx * 5) / 5
    x_coef = x_table[idx] + (x_table[idx + 1] - x_table[idx]) * frac
    y_coef = y_table[idx] + (y_table[idx + 1] - y_table[idx]) * frac
    return 0.8487 * x_coef * math.radians(lon), 1.3523 * sign * y_coef


def projected_point(lon, lat, box):
    x0, y0, x1, y1 = box
    px, py = robinson(lon, lat)
    min_x, max_x = -2.68, 2.68
    min_y, max_y = -1.36, 1.36
    x = x0 + ((px - min_x) / (max_x - min_x)) * (x1 - x0)
    y = y1 - ((py - min_y) / (max_y - min_y)) * (y1 - y0)
    return round(x, 1), round(y, 1)


def ring_to_path(ring, box):
    points = []
    for lon, lat in ring:
        if -180 <= lon <= 180 and -90 <= lat <= 90:
            points.append(projected_point(lon, lat, box))
    if len(points) < 3:
        return ""
    head, *tail = points
    commands = [f"M{head[0]} {head[1]}"]
    commands.extend(f"L{x} {y}" for x, y in tail)
    commands.append("Z")
    return " ".join(commands)


def build_map_paths(statuses):
    geojson = requests.get(
        "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson",
        timeout=30,
    ).json()
    box = (70, 330, 1010, 735)
    paths = []
    for feature in geojson["features"]:
        name = feature["properties"]["name"]
        if name == "Antarctica":
            continue
        record = statuses.get(name, {"status": "No", "funding_type": "-"})
        status = record["status"]
        funding_type = record["funding_type"].lower()
        if name == "Canada":
            css_class = "canada-solid"
        elif status == "Sub-jurisdictional":
            css_class = f"sub-{funding_type}" if funding_type in {"debt", "surplus", "hybrid"} else "sub-surplus"
        elif status == "Yes":
            css_class = f"funding-{funding_type}" if funding_type in {"debt", "surplus", "hybrid"} else "funding-debt"
        else:
            css_class = "land"
        geometry = feature["geometry"]
        polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
        for polygon in polygons:
            d = ring_to_path(polygon[0], box)
            if d:
                label = f"{name}: {funding_type.title()}" if status in {"Yes", "Sub-jurisdictional"} else name
                paths.append(f'<path class="{css_class}" d="{d}"><title>{html.escape(label)}</title></path>')
    return "\n          ".join(paths)


def build_leader_rows():
    rows = []
    for flag, fund, holdings, per_capita in LEADERS:
        rows.append(
            f"""
            <img class="leader-flag" src="../iOS Emoji Flags/{flag}.png" alt="" />
            <div class="leader-copy">
              <div class="leader-country">{html.escape(fund)}</div>
              <div class="leader-fund">{html.escape(holdings)}</div>
              <div class="leader-per-capita">{html.escape(per_capita)}</div>
            </div>
            """
        )
    return "\n".join(rows)


def build_html():
    statuses = load_statuses()
    map_paths = build_map_paths(statuses)
    leader_rows = build_leader_rows()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Sovereign Wealth Funds</title>
  <style>
    :root {{
      --paper: #F4EBE3;
      --ink: #1A1A1A;
      --muted: #6B6055;
      --rule: #C8BFB0;
      --red: #872D2E;
      --blue: #305E7E;
      --surplus: #305E7E;
      --surplus-light: #8ACCE4;
      --hybrid: #B54E1A;
      --hybrid-light: #F3C17B;
      --debt-light: #EBB1B1;
      --tan: #EDE5D5;
      --land: #EDE5D5;
      --water: #F4EBE3;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 18px;
      padding: 32px 0;
      background: #d8d0c6;
      color: var(--ink);
      font-family: "Test Söhne", "TestSöhne", Arial, sans-serif;
    }}

    .canvas {{
      position: relative;
      width: {WIDTH}px;
      height: {HEIGHT}px;
      padding: 68px 76px 58px;
      background: var(--paper);
      overflow: hidden;
    }}

    .canvas::before {{
      content: "";
      position: absolute;
      inset: 10px;
      border: 2px solid var(--ink);
      pointer-events: none;
    }}

    .header {{
      display: grid;
      grid-template-columns: 1fr 72px;
      gap: 24px;
      min-height: 132px;
      padding-bottom: 22px;
      border-bottom: 1px solid var(--rule);
    }}

    h1 {{
      max-width: 830px;
      margin: 0;
      font-size: 78px;
      line-height: 0.95;
      letter-spacing: -0.012em;
      font-weight: 760;
    }}

    .eyebrow {{
      margin-top: 14px;
      font-family: "Test Founders Grotesk", "TestFoundersGrotesk", "Test Founders Grotesk Text", "TestFoundersGroteskText", Arial, sans-serif;
      font-size: 18px;
      line-height: 1;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      font-weight: 700;
    }}

    .brand {{
      width: 72px;
      height: 72px;
      margin-top: 0;
      overflow: hidden;
      background: #C4A090;
      border: 1px solid rgba(26, 26, 26, 0.14);
    }}

    .brand img {{
      display: block;
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}

    .map-card {{
      margin-top: 22px;
      border-bottom: 1px solid var(--rule);
      padding-bottom: 22px;
    }}

    .map-frame {{
      width: 100%;
      height: 455px;
      border: 0;
      background: var(--water);
      overflow: hidden;
    }}

    .land {{
      fill: var(--land);
      stroke: #C8BFB0;
      stroke-width: 0.75;
    }}

    .funding-debt {{
      fill: var(--red);
      stroke: #743132;
      stroke-width: 0.75;
    }}

    .funding-surplus {{
      fill: var(--surplus);
      stroke: #244A63;
      stroke-width: 0.75;
    }}

    .canada-solid {{
      fill: var(--red);
      stroke: #743132;
      stroke-width: 0.75;
    }}

    .funding-hybrid {{
      fill: var(--hybrid);
      stroke: #8D3C16;
      stroke-width: 0.75;
    }}

    .sub-debt {{
      fill: url(#subDebtPattern);
      stroke: var(--red);
      stroke-width: 0.8;
    }}

    .sub-surplus {{
      fill: url(#subSurplusPattern);
      stroke: var(--surplus);
      stroke-width: 0.8;
    }}

    .sub-hybrid {{
      fill: url(#subHybridPattern);
      stroke: var(--hybrid);
      stroke-width: 0.8;
    }}

    .legend {{
      display: flex;
      justify-content: flex-end;
      gap: 28px;
      margin-top: -52px;
      font-family: "Test Founders Grotesk", "TestFoundersGrotesk", "Test Founders Grotesk Text", "TestFoundersGroteskText", Arial, sans-serif;
      font-size: 14px;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }}

    .legend-item {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
    }}

    .key {{
      width: 25px;
      height: 25px;
      background: var(--red);
    }}

    .key.surplus {{
      background: var(--surplus);
    }}

    .key.hybrid {{
      background: var(--hybrid);
    }}

    .key.sub-combo {{
      background:
        repeating-linear-gradient(45deg, transparent 0 7px, rgba(26, 26, 26, 0.34) 7px 9px),
        linear-gradient(90deg, var(--surplus) 0 33%, var(--red) 33% 66%, var(--hybrid) 66% 100%);
    }}

    .body-grid {{
      display: grid;
      grid-template-columns: 1fr 380px;
      gap: 44px;
      margin-top: 20px;
      align-items: start;
    }}

    .section-title {{
      margin: 0 0 14px;
      font-size: 43px;
      line-height: 1;
      letter-spacing: -0.035em;
      font-weight: 760;
    }}

    .leaderboard {{
      display: grid;
      grid-template-columns: 44px 1fr;
      border-top: 1px solid var(--rule);
    }}

    .leaderboard > div {{
      min-height: 100px;
      padding: 16px 0;
      border-bottom: 1px solid var(--rule);
      display: flex;
      flex-direction: column;
      justify-content: center;
    }}

    .leader-flag {{
      width: 32px;
      height: 32px;
      align-self: center;
      object-fit: contain;
    }}

    .leader-country {{
      font-family: "Test Founders Grotesk", "TestFoundersGrotesk", "Test Founders Grotesk Text", "TestFoundersGroteskText", Arial, sans-serif;
      font-size: 19px;
      line-height: 1;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      font-weight: 700;
    }}

    .leader-fund {{
      margin-top: 5px;
      color: var(--ink);
      font-family: "Test Founders Grotesk", "TestFoundersGrotesk", "Test Founders Grotesk Text", "TestFoundersGroteskText", Arial, sans-serif;
      font-size: 14px;
      line-height: 1.15;
      letter-spacing: 0.05em;
    }}

    .leader-per-capita {{
      margin-top: 3px;
      font-family: "Test Founders Grotesk", "TestFoundersGrotesk", "Test Founders Grotesk Text", "TestFoundersGroteskText", Arial, sans-serif;
      font-size: 14px;
      line-height: 1.15;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }}

    .callout {{
      min-height: 472px;
      padding: 27px 30px 26px;
      background: var(--red);
      border-radius: 18px;
      color: var(--paper);
    }}

    .callout h2 {{
      margin: 0 0 18px;
      color: var(--paper);
      font-size: 49.5px;
      line-height: 0.92;
      letter-spacing: -0.045em;
    }}

    .callout p {{
      margin: 0 0 14px;
      font-size: 16.5px;
      line-height: 1.35;
      font-weight: 560;
    }}

    .font-warning {{
      position: fixed;
      top: 24px;
      left: 50%;
      z-index: 1000;
      max-width: 560px;
      padding: 18px 22px;
      border: 2px solid var(--red);
      background: var(--tan);
      color: var(--ink);
      box-shadow: 0 10px 30px rgba(26, 26, 26, 0.18);
      font-family: Arial, sans-serif;
      font-size: 15px;
      line-height: 1.45;
      transform: translateX(-50%);
    }}

    .font-warning[hidden] {{ display: none; }}

    .font-warning strong {{
      display: block;
      margin-bottom: 4px;
      color: var(--red);
      font-size: 16px;
    }}

    .font-warning button {{
      margin-top: 12px;
      padding: 7px 12px;
      border: 1px solid var(--red);
      background: var(--red);
      color: var(--paper);
      font: inherit;
      cursor: pointer;
    }}

    .download-panel {{
      display: flex;
      justify-content: center;
      width: {WIDTH}px;
    }}

    .download-button {{
      border: 1px solid var(--ink);
      background: var(--ink);
      color: var(--paper);
      padding: 12px 18px 11px;
      font-family: "Test Founders Grotesk", "TestFoundersGrotesk", "Test Founders Grotesk Text", "TestFoundersGroteskText", Arial, sans-serif;
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      cursor: pointer;
    }}

    .download-button:disabled {{
      cursor: wait;
      opacity: 0.72;
    }}
  </style>
</head>
<body>
  <aside class="font-warning" id="font-warning" role="alert" hidden>
    <strong>Fallback fonts detected</strong>
    <span id="font-warning-message"></span>
    <button type="button" id="font-warning-dismiss">Dismiss</button>
  </aside>

  <main class="canvas" aria-label="Sovereign wealth fund world map and leaderboard">
    <header class="header">
      <div>
        <h1>Sovereign Wealth Funds</h1>
        <div class="eyebrow">More than a concept to watch from afar</div>
      </div>
      <div class="brand" aria-label="Build Canada logo">
        <img src="../Build Canada Logo.png" alt="Build Canada" />
      </div>
    </header>

    <section class="map-card" aria-label="World map of sovereign wealth funds">
      <svg class="map-frame" viewBox="0 0 1080 455" role="img" aria-label="Countries with sovereign wealth funds">
        <defs>
          <pattern id="subDebtPattern" patternUnits="userSpaceOnUse" width="14" height="14" patternTransform="rotate(45)">
            <rect width="14" height="14" fill="#EBB1B1"></rect>
            <line x1="0" y1="0" x2="0" y2="14" stroke="#872D2E" stroke-width="3"></line>
          </pattern>
          <pattern id="subSurplusPattern" patternUnits="userSpaceOnUse" width="14" height="14" patternTransform="rotate(45)">
            <rect width="14" height="14" fill="#8ACCE4"></rect>
            <line x1="0" y1="0" x2="0" y2="14" stroke="#305E7E" stroke-width="3"></line>
          </pattern>
          <pattern id="subHybridPattern" patternUnits="userSpaceOnUse" width="14" height="14" patternTransform="rotate(45)">
            <rect width="14" height="14" fill="#F3C17B"></rect>
            <line x1="0" y1="0" x2="0" y2="14" stroke="#B54E1A" stroke-width="3"></line>
          </pattern>
        </defs>
        <g transform="translate(540 238) scale(1.28) translate(-540 -532)">
          {map_paths}
        </g>
      </svg>
      <div class="legend" aria-label="Map legend">
        <span class="legend-item"><span class="key"></span>Debt-funded</span>
        <span class="legend-item"><span class="key surplus"></span>Surplus-funded</span>
        <span class="legend-item"><span class="key hybrid"></span>Hybrid-funded</span>
        <span class="legend-item"><span class="key sub-combo"></span>Sub-jurisdictional</span>
      </div>
    </section>

    <section class="body-grid">
      <div>
        <h2 class="section-title">Leaderboard</h2>
        <div class="leaderboard">
          {leader_rows}
        </div>
      </div>

      <aside class="callout">
        <h2>TL;DR</h2>
        <p>Sovereign wealth funds are generally used to park a country's excess wealth, usually from natural resources or trade surpluses, into global stocks, bonds, real estate, and infrastructure. The goal is to preserve and grow that wealth for future generations, stabilize government revenue during downturns, and reduce dependence on a single resource.</p>
        <p>With our vast oil and critical mineral wealth, Canada has been a natural candidate. A national sovereign wealth fund could do federally what Alberta's Heritage Fund does provincially: convert resource royalties into long-term financial assets.</p>
        <p>The recently announced Canada Strong Fund would be debt-funded, unlike most SWF's which use surplus-funding or hybrid models.</p>
      </aside>
    </section>
  </main>

  <div class="download-panel">
    <button class="download-button" type="button" id="download-png">Download PNG</button>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/html-to-image@1.11.11/dist/html-to-image.js"></script>
  <script>
    (() => {{
      const requiredFonts = [
        {{ name: "Test Söhne", families: ["Test Söhne", "TestSöhne"] }},
        {{
          name: "Test Founders Grotesk",
          families: [
            "Test Founders Grotesk",
            "TestFoundersGrotesk",
            "Test Founders Grotesk Text",
            "TestFoundersGroteskText"
          ]
        }}
      ];
      const sample = "Build Canada sovereign wealth fund 0123456789";

      function textWidth(fontFamily) {{
        const canvas = document.createElement("canvas");
        const context = canvas.getContext("2d");
        context.font = `48px ${{fontFamily}}`;
        return context.measureText(sample).width;
      }}

      function fontIsAvailable(fontFamilies) {{
        const fallbackFonts = ["Arial", "Times New Roman", "Courier New"];
        const fallbackWidths = fallbackFonts.map((fallback) => textWidth(fallback));

        return fontFamilies.some((fontFamily) => {{
          if (document.fonts && document.fonts.check(`16px "${{fontFamily}}"`)) {{
            return true;
          }}

          const quotedFont = `"${{fontFamily}}"`;
          const targetWidths = fallbackFonts.map((fallback) =>
            textWidth(`${{quotedFont}}, ${{fallback}}`)
          );

          return targetWidths.some((width, index) => width !== fallbackWidths[index]);
        }});
      }}

      function showWarning(missingFonts) {{
        const warning = document.getElementById("font-warning");
        const message = document.getElementById("font-warning-message");
        const dismiss = document.getElementById("font-warning-dismiss");

        message.textContent = `The required brand font${{missingFonts.length > 1 ? "s are" : " is"}} not in use: ${{missingFonts.join(", ")}}. The browser is rendering with fallback fonts.`;
        warning.hidden = false;
        dismiss.addEventListener("click", () => {{
          warning.hidden = true;
        }});
      }}

      window.addEventListener("load", () => {{
        const missingFonts = requiredFonts
          .filter((font) => !fontIsAvailable(font.families))
          .map((font) => font.name);

        if (missingFonts.length > 0) {{
          showWarning(missingFonts);
        }}
      }});

      const downloadButton = document.getElementById("download-png");
      downloadButton.addEventListener("click", async () => {{
        if (!window.htmlToImage) {{
          window.alert("PNG export library could not be loaded. Check your internet connection and try again.");
          return;
        }}

        downloadButton.disabled = true;
        const originalText = downloadButton.textContent;
        downloadButton.textContent = "Rendering...";

        try {{
          if (document.fonts && document.fonts.ready) {{
            await document.fonts.ready;
          }}

          const canvasElement = document.querySelector(".canvas");
          const dataUrl = await window.htmlToImage.toPng(canvasElement, {{
            backgroundColor: "#F4EBE3",
            cacheBust: true,
            canvasWidth: {WIDTH},
            canvasHeight: {HEIGHT},
            pixelRatio: 1,
            width: {WIDTH},
            height: {HEIGHT},
            style: {{
              margin: "0",
              transform: "none"
            }}
          }});

          const link = document.createElement("a");
          link.download = "sovereign-wealth-funds-2026.png";
          link.href = dataUrl;
          link.click();
        }} finally {{
          downloadButton.disabled = false;
          downloadButton.textContent = originalText;
        }}
      }});
    }})();
  </script>
</body>
</html>
"""


def main():
    OUTPUT_PATH.write_text(build_html(), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
