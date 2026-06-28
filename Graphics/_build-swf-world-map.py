"""Bake sovereign wealth fund world map SVG paths into HTML."""
import html
import json
import math
import re
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "Graphics" / "article-assets" / "sovereign-wealth-funds" / "country-status.json"
OUTPUT_PATH = ROOT / "Graphics" / "sovereign-wealth-funds-world-map-2026.html"

WIDTH = 1350
HEIGHT = 1080

WORLD_GEOJSON_URL = (
    "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson"
)
ADMIN1_GEOJSON_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
    "geojson/ne_50m_admin_1_states_provinces.geojson"
)

# Projection box — wide landscape crop; viewBox is tightened to path bounds after bake.
MAP_BOX = (12, 6, 1338, 674)
MAP_TRANSFORM = ""
VIEWBOX_PAD = 6

GEO_ALIASES = {
    "United Kingdom": "England",
    "United States": "USA",
    "Timor-Leste": "East Timor",
}

# Micro-states missing from holtzy world.geojson (lon, lat, radius in degrees).
MICRO_STATES = {
    "Bahrain": (50.55, 26.07, 0.35),
    "Kiribati": (173.0, 1.42, 0.55),
    "Singapore": (103.82, 1.35, 0.28),
}


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
    # Crop projection latitude to inhabited land so the map fills vertical space.
    _, min_y = robinson(0, -58)
    _, max_y = robinson(0, 84)
    x = x0 + ((px - min_x) / (max_x - min_x)) * (x1 - x0)
    y = y1 - ((py - min_y) / (max_y - min_y)) * (y1 - y0)
    return round(x, 1), round(y, 1)


def ring_to_path(ring, box, close=True):
    points = []
    for lon, lat in ring:
        if -180 <= lon <= 180 and -90 <= lat <= 90:
            points.append(projected_point(lon, lat, box))
    if len(points) < 3:
        return ""
    head, *tail = points
    commands = [f"M{head[0]} {head[1]}"]
    commands.extend(f"L{x} {y}" for x, y in tail)
    if close:
        commands.append("Z")
    return " ".join(commands)


def circle_path(lon, lat, radius_deg, box, segments=16):
    points = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        d_lon = lon + radius_deg * math.cos(angle)
        d_lat = lat + radius_deg * math.sin(angle)
        points.append(projected_point(d_lon, d_lat, box))
    head, *tail = points
    commands = [f"M{head[0]} {head[1]}"]
    commands.extend(f"L{x} {y}" for x, y in tail)
    commands.append("Z")
    return " ".join(commands)


def path_d_values(path_elements):
    for element in path_elements:
        match = re.search(r'\sd="([^"]+)"', element)
        if match:
            yield match.group(1)


def coords_from_d(d):
    return [
        (float(x), float(y))
        for x, y in re.findall(r"[ML](-?\d+\.?\d*)\s+(-?\d+\.?\d*)", d)
    ]


def compute_viewbox(path_elements, pad=VIEWBOX_PAD):
    xs, ys = [], []
    for d in path_d_values(path_elements):
        for x, y in coords_from_d(d):
            xs.append(x)
            ys.append(y)
    if not xs:
        return f"0 0 {WIDTH} 700"
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    return (
        f"{min_x - pad:.1f} {min_y - pad:.1f} "
        f"{max_x - min_x + 2 * pad:.1f} {max_y - min_y + 2 * pad:.1f}"
    )


def polygon_paths(geometry, box, close=True):
    if geometry["type"] == "Polygon":
        polygons = [geometry["coordinates"]]
    else:
        polygons = geometry["coordinates"]
    paths = []
    for polygon in polygons:
        d = ring_to_path(polygon[0], box, close=close)
        if d:
            paths.append(d)
    return paths


def load_data():
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def country_lookup(data):
    lookup = {}
    for name, record in data["countries"].items():
        geo_name = GEO_ALIASES.get(name, name)
        lookup[geo_name] = {"canonical": name, **record}
    return lookup


def build_country_paths(world_geojson, lookup):
    paths = []
    for feature in world_geojson["features"]:
        name = feature["properties"]["name"]
        if name == "Antarctica":
            continue
        record = lookup.get(name)
        if record:
            funding = record["funding"]
            css_class = f"funding-{funding}"
            label = f"{record['canonical']}: {funding.title()}"
        else:
            css_class = "land"
            label = name
        for d in polygon_paths(feature["geometry"], MAP_BOX):
            paths.append(
                f'<path class="{css_class}" d="{d}">'
                f"<title>{html.escape(label)}</title></path>"
            )
    for name, record in lookup.items():
        if name in MICRO_STATES:
            lon, lat, radius = MICRO_STATES[name]
            funding = record["funding"]
            css_class = f"funding-{funding}"
            label = f"{record['canonical']}: {funding.title()}"
            d = circle_path(lon, lat, radius, MAP_BOX)
            paths.append(
                f'<path class="{css_class}" d="{d}">'
                f"<title>{html.escape(label)}</title></path>"
            )
    return paths


def build_sub_paths(admin_geojson, sub_jurisdictions):
    paths = []
    for sub_name, record in sub_jurisdictions.items():
        funding = record["funding"]
        css_class = f"sub-{funding}"
        admin = record.get("admin", record["parent"])
        label = f"{sub_name} ({record['parent']}): {funding.title()}"
        matched = False
        for feature in admin_geojson["features"]:
            props = feature["properties"]
            feat_name = props.get("name") or props.get("name_en") or ""
            feat_admin = props.get("admin") or props.get("adm0_name") or ""
            if feat_name != sub_name:
                continue
            if admin not in feat_admin and feat_admin not in admin:
                if record["parent"] == "United States" and feat_admin != "United States of America":
                    continue
                if record["parent"] == "Canada" and feat_admin != "Canada":
                    continue
            matched = True
            for d in polygon_paths(feature["geometry"], MAP_BOX):
                paths.append(
                    f'<path class="{css_class}" d="{d}">'
                    f"<title>{html.escape(label)}</title></path>"
                )
        if not matched:
            print(f"WARNING: no geometry match for sub-jurisdiction {sub_name}")
    return paths


def build_html(country_paths, sub_paths, viewbox):
    country_block = "\n          ".join(country_paths)
    sub_block = "\n          ".join(sub_paths)
    if MAP_TRANSFORM:
        map_inner = f"""<g transform="{MAP_TRANSFORM}">
          {country_block}
          {sub_block}
        </g>"""
    else:
        map_inner = f"{country_block}\n          {sub_block}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Sovereign wealth funds world map</title>
  <link rel="stylesheet" href="brand-fonts.css" />
  <style>
    :root {{
      --paper: #F4EBE3;
      --ink: #1A1A1A;
      --muted: #6B6055;
      --rule: #C8BFB0;
      --red: #872D2E;
      --blue: #305E7E;
      --hybrid: #B54E1A;
      --tan: #EDE5D5;
      --land: #EDE5D5;
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
      font-synthesis: none;
    }}

    .canvas {{
      position: relative;
      width: {WIDTH}px;
      height: {HEIGHT}px;
      padding: 28px 40px 18px;
      background: var(--paper);
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}

    .canvas::before {{
      content: "";
      position: absolute;
      inset: 10px;
      border: 2px solid var(--ink);
      pointer-events: none;
      z-index: 4;
    }}

    .canvas > * {{
      position: relative;
      z-index: 2;
    }}

    .header {{
      display: grid;
      grid-template-columns: 1fr 68px;
      gap: 18px;
      align-items: start;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--rule);
      flex-shrink: 0;
    }}

    .mono {{
      margin: 0 0 6px;
      font-family: "Test Söhne Mono", "TestSöhneMono", "TESTSÖHNEMONO", "Roboto Mono", monospace;
      font-size: 17px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-weight: 600;
      color: var(--muted);
      line-height: 1.2;
    }}

    h1 {{
      max-width: 1120px;
      margin: 0;
      font-size: 42px;
      line-height: 1.04;
      letter-spacing: -0.02em;
      font-weight: 760;
      color: var(--ink);
    }}

    .brand {{
      width: 68px;
      height: 68px;
      background: var(--paper);
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .brand img {{
      display: block;
      width: 100%;
      height: 100%;
      object-fit: contain;
    }}

    .map-section {{
      flex: 1 1 auto;
      min-height: 0;
      position: relative;
      margin-top: 6px;
    }}

    .map-frame {{
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      display: block;
      background: var(--paper);
      overflow: visible;
    }}

    .land {{
      fill: var(--land);
      stroke: #C8BFB0;
      stroke-width: 0.7;
    }}

    .funding-debt {{
      fill: var(--blue);
      stroke: #244A63;
      stroke-width: 0.75;
    }}

    .funding-surplus {{
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
      stroke: var(--blue);
      stroke-width: 0.75;
    }}

    .sub-surplus {{
      fill: url(#subSurplusPattern);
      stroke: var(--red);
      stroke-width: 0.75;
    }}

    .sub-hybrid {{
      fill: url(#subHybridPattern);
      stroke: var(--hybrid);
      stroke-width: 0.75;
    }}

    .legend {{
      position: absolute;
      left: 0;
      bottom: 4px;
      z-index: 3;
      display: flex;
      flex-wrap: wrap;
      justify-content: flex-start;
      gap: 16px 22px;
      margin: 0;
      padding: 5px 10px;
      background: rgba(244, 235, 227, 0.94);
      font-family: "Test Founders Grotesk", "TestFoundersGrotesk", "Test Founders Grotesk Text", "TestFoundersGroteskText", Arial, sans-serif;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }}

    .legend-item {{
      display: inline-flex;
      align-items: center;
      gap: 9px;
    }}

    .key {{
      width: 22px;
      height: 22px;
      flex-shrink: 0;
    }}

    .key.debt {{ background: var(--blue); }}
    .key.surplus {{ background: var(--red); }}
    .key.hybrid {{ background: var(--hybrid); }}

    .key.sub {{
      background:
        repeating-linear-gradient(45deg, transparent 0 5px, rgba(26, 26, 26, 0.28) 5px 6px),
        var(--land);
      border: 1px solid var(--rule);
    }}

    .footer {{
      margin-top: 6px;
      padding-top: 8px;
      border-top: 1px solid var(--rule);
      flex-shrink: 0;
      font-family: "Test Founders Grotesk", "TestFoundersGrotesk", "Test Founders Grotesk Text", "TestFoundersGroteskText", Arial, sans-serif;
      font-size: 12px;
      line-height: 1.45;
      color: var(--muted);
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

  <main class="canvas" id="graphic" aria-label="World map of sovereign wealth funds by funding model">
    <header class="header">
      <div>
        <p class="mono">Global pattern</p>
        <h1>Sovereign wealth funds are already global</h1>
      </div>
      <div class="brand" aria-label="Build Canada logo">
        <img src="../Build Canada Logo.png" alt="Build Canada" />
      </div>
    </header>

    <section class="map-section" aria-label="World map">
      <svg class="map-frame" viewBox="{viewbox}" preserveAspectRatio="xMidYMin meet" role="img" aria-label="Countries with sovereign wealth funds highlighted by funding type">
        <defs>
          <pattern id="subDebtPattern" patternUnits="userSpaceOnUse" width="12" height="12" patternTransform="rotate(45)">
            <rect width="12" height="12" fill="#B8CDDD"></rect>
            <line x1="0" y1="0" x2="0" y2="12" stroke="#305E7E" stroke-width="2.5"></line>
          </pattern>
          <pattern id="subSurplusPattern" patternUnits="userSpaceOnUse" width="12" height="12" patternTransform="rotate(45)">
            <rect width="12" height="12" fill="#D4A0A1"></rect>
            <line x1="0" y1="0" x2="0" y2="12" stroke="#872D2E" stroke-width="2.5"></line>
          </pattern>
          <pattern id="subHybridPattern" patternUnits="userSpaceOnUse" width="12" height="12" patternTransform="rotate(45)">
            <rect width="12" height="12" fill="#E8B896"></rect>
            <line x1="0" y1="0" x2="0" y2="12" stroke="#B54E1A" stroke-width="2.5"></line>
          </pattern>
        </defs>
        {map_inner}
      </svg>
      <div class="legend" aria-label="Map legend">
        <span class="legend-item"><span class="key debt"></span>Debt-funded</span>
        <span class="legend-item"><span class="key surplus"></span>Surplus-funded</span>
        <span class="legend-item"><span class="key hybrid"></span>Hybrid-funded</span>
        <span class="legend-item"><span class="key sub"></span>Sub-jurisdictional</span>
      </div>
    </section>

    <footer class="footer">
      Sources: Global SWF and SWFI sovereign wealth fund trackers (2025-2026). Wikipedia, List of sovereign wealth funds (accessed Jun. 2026). Finance Canada and PMO, Canada Strong Fund announcement (Apr. 2026). UK National Wealth Fund and HM Treasury (2024-2025).
    </footer>
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
        dismiss.addEventListener("click", () => {{ warning.hidden = true; }});
      }}

      window.addEventListener("load", () => {{
        const missingFonts = requiredFonts
          .filter((font) => !fontIsAvailable(font.families))
          .map((font) => font.name);
        if (missingFonts.length > 0) showWarning(missingFonts);
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
          if (document.fonts && document.fonts.ready) await document.fonts.ready;
          const canvasElement = document.getElementById("graphic");
          const dataUrl = await window.htmlToImage.toPng(canvasElement, {{
            backgroundColor: "#F4EBE3",
            cacheBust: true,
            canvasWidth: {WIDTH},
            canvasHeight: {HEIGHT},
            pixelRatio: 1,
            width: {WIDTH},
            height: {HEIGHT},
            style: {{ margin: "0", transform: "none" }}
          }});
          const link = document.createElement("a");
          link.download = "sovereign-wealth-funds-world-map-2026.png";
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
    data = load_data()
    lookup = country_lookup(data)
    print("Fetching world GeoJSON...")
    world = requests.get(WORLD_GEOJSON_URL, timeout=60).json()
    print("Fetching admin-1 GeoJSON...")
    admin1 = requests.get(ADMIN1_GEOJSON_URL, timeout=60).json()

    country_paths = build_country_paths(world, lookup)
    sub_paths = build_sub_paths(admin1, data["sub_jurisdictions"])
    print(f"Countries: {len(country_paths)} paths, Sub-jurisdictions: {len(sub_paths)} paths")

    viewbox = compute_viewbox(country_paths + sub_paths)
    print(f"ViewBox: {viewbox}")

    html_out = build_html(country_paths, sub_paths, viewbox)
    OUTPUT_PATH.write_text(html_out, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
