# Spring Economic Update — “Builder’s POV” graphic format

Notes for **`spring-economic-update-encouraging-2026.html`** and any sibling graphics that reuse this layout.

---

## Purpose

Single-page infographic: headline plus **numbered policy sections** (verbatim excerpts from the Spring Economic Update), Build Canada commentary (“Why we like it”), and a **consulting bar comparison** in the last section. Intended export: **PNG** at canvas size via **html-to-image**.

---

## Canvas & frame

| Property | Value |
|----------|--------|
| Size | **1080 × 1350px** (`.canvas`) |
| Background | Parchment **`#F4EBE3`** (`--paper`) |
| Inner outline | **2px solid** **`#1A1A1A`** (`--ink`), **`::before`** inset **10px** on all sides |
| Padding | Roughly **36px / 56px / 26px** (top / sides / bottom) |

There is **no horizontal rule above the footer / Sources line** in this variant—sources sit flush below the policy stack with spacing only (`margin-top` / `padding-top` on `.footer`).

---

## Header

- **Mono line** (Test Söhne Mono): deck context (“Spring economic update · …”). Uppercase, muted grey (`--muted`).
- **`h1`**: Main title (**Spring Economic Update from a Builder’s POV**). Test Söhne, **`white-space: nowrap`**, fluid sizing via **`clamp`** + **`cqw`** against the header container. Letter-spacing tuned for readability (slightly open vs tight tracking).
- **Logo**: Top-right; **`Build Canada Logo.png`** from repo root (`../Build Canada Logo.png`).
- **Divider**: Thin **`border-bottom`** on `.header` (`--rule`), separating header from body—not duplicated above the footer.

---

## Body: policy stack

Sections are **`article.policy-section`** cards:

- **Grid**: Narrow rail (**~46px**) + main column.
- **Rail** (`.policy-marker`): Red **section index** + **Heroicons** outline SVG from jsDelivr (MIT), stacked vertically.
- **Card chrome**: **Rounded rectangle** (`border-radius ~14px`), light warm-grey **border**, translucent white fill, light shadow.
- **Label** (`.policy-label`): Test Founders Grotesk, uppercase, tight **letter-spacing** (~`0.035em`), muted colour.
- **Excerpts**: `blockquote.policy-quote` with **left red rule**—policy text should stay **verbatim**; **`cite`** URLs point at source pages/PDF sections.
- **Commentary**: `.copy.compact` with **“Why we like it:”** in brand red.

**Section order (as of this file):**

1. Competition  
2. Housing  
3. SR&ED  
4. Procurement  
5. CRA rulings  
6. **Consulting** (last)—includes projection line and chart.

Within **Consulting**, order is: excerpts → why we like it → projection numbers → chart.

---

## Consulting chart

- Two columns: **prior** vs **after** envelope; shared vertical scale; **dashed “Savings”** band on the after column.
- Colours: **`--red`** (prior bar), **`--blue`** (after), muted rules/captions.
- Bar/track sizes are **scoped** under **`.policy-section--chart .consult-chart`** so global chart classes do not fight other graphics.
- Chart value labels (e.g. `$2.25B`): positive **letter-spacing** for legibility.

---

## Footer

- Small Test Founders Grotesk, muted, **no top border** in this format.
- Typical text: Government of Canada SEU attribution + “Analysis, Build Canada.”

---

## PNG export

- **Download** control lives **outside** `#export-root` (only the `.canvas` exports).
- **`html-to-image`** `toPng`, fixed **1080×1350**, parchment background colour passed in.
- Wait on **`document.fonts.ready`** and **heroicon `<img>` loads** before capture.

---

## Fonts & QA

- **Required**: Test Söhne, Test Founders Grotesk (with alias names in stacks—see **`designprinciples.md`**).
- **Fallback warning**: `#font-warning` if detection decides brand fonts are not active.

---

## Related doc

Broader Build Canada rules (palette, typography philosophy, legacy table layouts): **`designprinciples.md`** at repo root. This SEU graphic intentionally diverges where noted above (e.g. **black** inset frame, **numbered cards** instead of a three-column comparison table, **no** footer rule).
