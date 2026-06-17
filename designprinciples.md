# Build Canada — Visual Design Principles

A reference guide for AI systems generating infographics, reports, and data visualizations consistent with the Build Canada brand.

---

## Colour Palette

- **Background:** Warm parchment — `#F4EBE3`. Always use this exact value. Never pure white or cool grey.
- **Primary text:** Deep charcoal-black — `#1A1A1A` or near-black. Not pure `#000000`.
- **Accent / heading colour:** Build Canada red — `#872D2E`. Used for primary display headings, key labels, and emphasis. Always use this exact value.
- **Secondary accents (choose one per graphic — do not mix):**
  - `#305E7E` — steel blue (first preference)
  - `#B54E1A` — burnt orange
  - `#7B24CB` — purple
  - `#2E7935` — forest green
- **Tertiary / supporting tints (used for fills, highlights, and backgrounds — paired with their secondary counterpart):**
  - `#EBB1B1` — soft rose (pairs with Build Canada red `#872D2E`)
  - `#8ACCE4` — light blue (pairs with `#305E7E`)
  - `#F3C17B` — warm amber (pairs with `#B54E1A`)
  - `#D6B5FC` — lavender (pairs with `#7B24CB`)
  - `#97E8A4` — mint (pairs with `#2E7935`)
- **Highlight fill (key difference rows):** Very light warm tan — `#EDE5D5` or similar, used as a subtle background on emphasised rows or callout sections.
- **Page / canvas outline:** The visible frame around the graphic is **black** — use **`#1A1A1A`** (same as primary text; not brand red). **2px** solid, inset **10px** from each canvas edge. Do not use `#872D2E` for this outer frame unless a piece explicitly calls for a red edge treatment.
- **Rose-taupe in the printed mark (~`#C4A090`):** The logo PNG may include this as narrow vertical accent bars beside the central red square. Treat that appearance as coming from **the asset only** — see **Brand Mark** for the HTML rule (do not paint a second taupe square behind the PNG).
- **Dividers and rules:** Thin lines in mid-warm grey — `#C8BFB0` or similar.
- **Funding-type map colours:** When a sovereign wealth fund map distinguishes funding models, use `#305E7E` steel blue for debt-funded funds, `#872D2E` Build Canada red for surplus-funded funds, and `#B54E1A` burnt orange for hybrid-funded funds.
- **Sub-jurisdictional map patterns:** When a country is sub-jurisdictional, keep the hatch/pattern treatment and apply the hatch colour based on that entry's funding type. The legend swatch for "sub-jurisdictional" should communicate that it can combine all funding colours, not imply a fourth standalone category colour.

---

## Typography

- **Primary typeface — Test Söhne:** Used for H1 headlines, subheadings, and all body copy / longer-form text. This is the default typeface for the majority of text in any graphic.
- **Label typeface — Test Founders Grotesk:** Used for brief, discrete lines of text — row labels, column headers, captions, tags, badges, and any short UI-style copy. Do not use for sentences or paragraphs.
- **Editorial typeface — Test Financier:** Optional. Use only when explicitly specified as the typeface for a piece. Suited to longer-form editorial or report copy where a serif voice is appropriate.
- **Do not substitute** system fonts, Google Fonts, or fallback sans-serifs. If a specified typeface is unavailable, flag it rather than silently substituting.
- **Fallback-font warning:** HTML graphics must include a visible popup warning if any required brand font is not actually in use and the browser has fallen back to Arial or another sans-serif. The warning should name the missing font(s) and remain visible until dismissed.
- **Repo fonts (`fonts/`):** Brand OTFs live in the project `fonts/` directory. HTML graphics in `Graphics/` must `<link rel="stylesheet" href="brand-fonts.css" />` so the browser loads faces from `../fonts/` (works on `http://localhost`; `file://` often blocks font files). Do not rely on Windows system font names alone — aliases like `TestSöhne` / `TESTSÖHNE` often still render as Arial.
- **Installed font aliases:** In `font-family` stacks after the primary name, you may keep `"TestSöhne"` and Founders text aliases as fallbacks. Windows may list files such as `TESTSÖHNE-BUCH_0.OTF` under Settings → Fonts → **Test Söhne**; that folder name is the family, not the filename. Use brand CSS weights **520** (body) and **760** (display), mapped in `brand-fonts.css` to Buch and Dreiviertelfett files in `fonts/`.
- **Display / hero headline:** Large, bold weight of Test Söhne. Left-aligned. Set in near-black. Size roughly 2.5–3× body text. Sentence case, not all-caps.
- **Header zone type scale (mandatory dominance):** Everything in the header zone — mono kicker, hero headline (H1), and any deck/subhead directly under it — must be **substantially larger** than body copy, chart labels, and dense body modules (table cells, list items, and similar) on the same canvas. Headers should read clearly at thumbnail scale (e.g. social feeds). Do **not** shrink kicker/H1/deck to make room for denser body content; reduce body density instead. For the default **1080×1350px** canvas, treat these as typical floors (adjust upward for short titles): Test Söhne Mono kicker **≥16px** (often **17–18px**); hero H1 **≥48px** (often **52–56px** for multi-line headlines); deck/subhead in Test Söhne **≥20px** (often **21–23px**) when present. Scale the brand mark up slightly with a larger headline so the block does not feel top-heavy toward the logo.
- **Mono lines:** Any line set in Test Söhne Mono, including short deck/kicker lines and source notes, should be all caps. Use modest tracking. For mono deck/kicker lines under the hero headline, keep the line close to the first divider: approximately 10px above the mono line, 8px below it to the divider, and no forced header minimum height.
- **Display tracking:** Hero headlines may use slight negative tracking, but avoid overly tight letter spacing. If the title feels cramped, open the tracking by a few points rather than shrinking the type.
- **Section labels (e.g. "INITIAL SIZE", "GOVERNANCE"):** Test Founders Grotesk. Uppercase with tracking, body weight, in charcoal. Paired with an icon to the left. On the standard **1080×1350px** canvas, prefer **≥11px** CSS (often **12px**) so labels survive mobile and feed scaling; for chart-first or phone-targeted pieces use **≥16px** (often **17–18px**) on section titles, axis labels, and legends. Denser print-style pieces may go smaller only when explicitly requested.
- **Column headers (document/source labels):** Test Founders Grotesk. Uppercase, widely tracked — `#6B6055` warm grey. On the standard canvas prefer **≥10px**, typically **11px** CSS.
- **Primary data figures (e.g. "$25B"):** Extra-bold weight of Test Söhne, oversized — clearly larger than adjacent body lines (typically **~2.5×** body CSS size or more on feed-facing graphics). In comparison tables, set `#872D2E` for the primary or government column and the chosen secondary accent for the alternate column. In other layouts, reserve `#872D2E` for the most important fiscal or headline figures and use the single chosen secondary accent for a second tier if needed. Apply **slight positive letter-spacing** (about **0.02em–0.03em** CSS `letter-spacing`) on numeric callouts so digits stay distinct when the graphic is scaled down — avoid tight negative tracking on oversized figures (hero headlines may still use modest negative tracking per **Display tracking** above).
- **Body / cell text:** Regular weight Test Söhne, dark charcoal. Comfortable line-height (~1.45–1.5). No italic unless distinguishing a source or caption. For default **1080×1350px** HTML graphics meant for phones and social feeds, target **14–17px** CSS — legible after downscaling — unless the brief explicitly demands maximum density (then smaller sizes are acceptable). Applies to table cells, list bodies, and narrative blocks alike.
- **Caption / source text:** Test Founders Grotesk, warm grey. Runs along the bottom at full width. On the standard canvas use **≥11px**, preferably **12px** CSS — sources must remain readable on small screens, not footnote-sized. **Do not use hyperlinks** (`<a>` tags, underlined URLs, or clickable links) in source lines on the graphic. Cite organisation, document title, and date as **plain text** only. Full canonical URLs may appear as plain strings without styling as links only when the brief requires traceability — otherwise titles and dates suffice.
- **Semantic type scale (`Graphics/brand-type-scale.css`):** Link after `brand-fonts.css` and add `type-scale` plus an aspect class on the canvas: `type-scale--portrait` for **1080×1350**, `type-scale--square` for **1080×1080** content slides (not hero/cover). Use semantic elements where possible: `h1` hero, `h2` section titles, `h3` row/chart labels, `p` body. Utility classes for exceptions: `type-deck`, `type-body-lg`, `type-stat`, `type-pullquote`, `type-lead`, `type-caption`, `type-chart-label`, `type-attribution`. Cover/teaser hero blocks keep bespoke sizes and are outside this scale.

  | Role | Portrait | Square (carousel body) |
  |------|----------|------------------------|
  | Mono kicker | 17px | 24px |
  | H1 | 52px | 56px |
  | H2 (Founders caps) | 16px | 20px |
  | H3 (Founders caps) | 14px | 18px |
  | Deck / body-lg | 26px / 22px | 32px (body-lg) |
  | Body | 17px | 26px |
  | Stat | 44px | 30px (34px badge nums) |
  | Chart label | 11px | 16px |
  | Footer / caption | 12px | 14px footer, 22px caption |

- **Cross-platform legibility:** Assume every graphic will be viewed on phones and in compressed thumbnails. **The bar for chart-heavy and data graphics is readability on a phone at full width without pinch-zooming** — axis labels, legend text, bar values, and section titles must stay legible after the 1080px canvas scales down to a typical mobile viewport (~360–430px wide). Scale **all** tiers together (header, labels, body, stats, footer): add whitespace and reduce chart density before shrinking type below the floors above. For multi-chart canvases, put the primary chart first (top), leave generous vertical gaps between blocks, stack legends when horizontal space is tight, and prefer fewer, larger elements over cramming. Numeric callouts should still visually dominate adjacent prose.

---

## Layout & Grid

- **Canvas:** Portrait orientation. Default size is **1080×1350px**. Always use this unless a different size is explicitly requested.
- **Output format:** Always produce graphics as **HTML files** unless another format is explicitly requested.
- **Authoring approach:** Prefer directly editable, hand-authored HTML/CSS/JS for individual graphics. Avoid using Python or other generator scripts unless they are genuinely necessary for large data transformations, complex map geometry, repeated batch output, or reproducibility that would be impractical by hand.
- **No raster-only deliverables:** Do not stop at PNG/JPG output for a graphic. If a bitmap preview or export is created, the editable HTML file remains the primary deliverable and must be created first.
- **PNG export control:** HTML graphics should include a centered "Download PNG" button below the graphic when practical. The button must sit outside the 1080×1350 canvas and export only the graphic canvas, not the button or surrounding page chrome, matching the browser-rendered appearance as closely as possible.
- **PNG export fidelity:** Prefer browser/SVG `foreignObject`-style export libraries for PNG downloads when typography must match the live preview. Avoid export paths that repaint text with noticeably different font weights.
- **Border:** A **2px** solid outline in **black (`#1A1A1A`)** runs around the inside edge of the canvas, inset exactly **10px** from each edge. This frames the parchment field (see Colour Palette — page/canvas outline). **Default is not brand red** for this frame unless a graphic brief explicitly requests a brick-red edge.
- **Outer margin:** Wide — approximately 6–8% of canvas width on all sides, measured from inside the border.
- **Header zone:** Top ~25% of the canvas. Contains the hero headline (left) and the brand tile (top right). No body content in this zone. Typography here must follow **Header zone type scale** under Typography — visibly larger than all non-header text on the graphic.
- **Divider rule:** A thin full-width horizontal rule separates the header from the content body.
- **Content body and format:** The area below the header divider is **not** locked to one layout pattern. **Choose the structure that fits the brief and the story** (comparison table, numbered list, timeline, stat strip, chart-first block, map plus legend, single-column editorial stack, or a hybrid). Use a **comparison table** when readers need to scan two positions, proposals, or options in parallel. Use a **list or narrative stack** when the message is sequential, conditional, or accountability-style. Use **charts or maps** when the evidence is inherently spatial or quantitative. Keep hierarchy, spacing, and type scales consistent with the rest of this guide regardless of format.
- **Comparison table (when used):** Three columns — a narrow left column for row icons and labels, a middle column for one entity/option, and a right column for the second entity/option. Column widths approximately 18% / 41% / 41%.
- **Table rows (when used):** Each row has a fixed-height zone. Rows are separated by thin horizontal rules in warm grey. No heavy borders or box shadows.
- **Highlighted rows or callouts (when used):** A single emphasised row or block may use a light warm tan fill (`#EDE5D5`) to draw attention. Label with a small "KEY DIFFERENCE" badge in brick red when the piece is comparative, or a short Founders Grotesk label when it is not.
- **Footer:** A thin rule above. Source citations in warm-grey plain text, full width — match **Caption / source** sizing (prefer **12px** CSS on the standard canvas). No `<a>` elements or link styling on the exported canvas.
- **Hero-and-body teaser (square / social):** Layouts with a fixed-height **hero** image or band and a **body** block below (mono kicker, H1, optional deck) must keep the **source row** (horizontal rule + attribution + optional small mark) **pinned to the bottom** of the body column, like the NATO CTV square reference (`ctv-nato-surveillance-square-2026.html`). Implement the body as a **column flex** container with **`flex: 1 1 auto`** (and `min-height: 0` where needed) on the **deck / summary** element so extra vertical space accumulates **between** the deck and the footer, not below the footer. Short copy must not leave the footer **floating** mid-canvas.
- **Publisher badge (hero-and-body teaser):** When a square/social teaser places the **source publisher logo** on the hero image (see `cbc-federal-ai-strategy-square-2026.html`, `ctv-nato-surveillance-square-2026.html`), prepare the logo asset **before** layout — do not tune padding by eye with CSS transforms or overflow clip boxes.
  - **Pixel-scan crop (required for raster logos):** Scan the source logo for non-background pixels (treat RGB **≥250** on all channels as background unless the brief says otherwise). Compute the tight bounding box, crop to it, and save to `Graphics/article-assets/` as `{publisher}-logo-cropped.png`. Use this cropped file in the HTML — not the original download with baked-in margins.
  - **Vector exception:** SVG logos with clean viewBox bounds (e.g. `ctv-news-official.svg`, `nrcan-logo.svg`) may ship as-is; still use equal CSS padding — no scale hacks.
  - **Badge styling:** White `#ffffff` container, **2px** border-radius, shadow `0 1px 4px rgba(0, 0, 0, 0.28)`, top-left on hero (~**22px** inset). **Equal padding on all sides** via CSS `padding` only — default **10px**. Do **not** use `transform: scale`, fixed inner clip dimensions, or asymmetric padding to compensate for source-file whitespace.
  - **Logo display size:** Cropped mark at **48px** CSS height, `width: auto`, `object-fit: contain`. Scale padding and height together if a brief asks for a larger or smaller badge — keep padding equal on all sides.
  - **Reusable crop snippet (Python / Pillow):** Open source image → iterate pixels → record min/max `x`/`y` where any channel **<250** → `img.crop((min_x, min_y, max_x + 1, max_y + 1))` → save PNG. Re-run when the source logo file changes.
  - **Reference:** `cbc-federal-ai-strategy-square-2026.html` + `article-assets/cbc-news-logo-cropped.png`.
- **Overflow check:** Before considering an HTML graphic complete, verify the rendered canvas at **1080×1350px** (or the requested aspect). No text, chart, legend, footer, image, or callout may cross the **inner black frame** or be clipped by the bottom edge.
- **Map framing:** Maps should be zoomed/framed to the data region so landmasses occupy the available chart area. Avoid large unused ocean margins unless they are essential to geographic context.
- **Map background:** For world maps in this style, default the ocean/background fill to the same warm parchment as the canvas unless the user explicitly asks for a water-colour treatment. This prevents a boxed-off map panel from feeling disconnected from the page.
- **Map legends:** Keep map legends close to the map, especially when the map background matches the canvas. Do not leave a large blank band between the map and its legend.

---

## Country Flags

- **When to use:** Any chart, table, or graphic comparing Canada to other countries must include that country's flag somewhere prominent — adjacent to the country name or as a column/row header.
- **Flag files:** Do not use system/default text emoji flags. Use the PNG emoji-style flag pack located in the **"iOS Emoji Flags"** folder in the directory. Files follow the two-letter ISO 3166-1 alpha-2 naming scheme (e.g. `CA.png` for Canada, `US.png` for the United States, `DE.png` for Germany).
- **Canada's flag** (`CA.png`) should always be included when other countries are present, even if Canada is the default/baseline column.
- **Size and placement:** Flags should be rendered at a consistent size across all entries in the same graphic — typically 24–32px tall. Align them uniformly (left of label or centred above column header).
- **Do not:** Stretch flags, apply filters or colour overlays, or mix PNG flags with any system emoji flags in the same graphic.

---

## Iconography

- **Style:** Simple line icons from a single library family per graphic (Icons8 iOS line style is the default). Approximately 20–24px at standard resolution; scale up proportionally on card or carousel layouts.
- **Source (required):** **Always** use icon image assets from an online library (Icons8, Noun Project, or equivalent). **Never** hand-draw custom inline SVG icons for row labels, section headings, cards, or list items. Inline SVG is reserved for structural diagram elements (connectors, charts, maps) — not pictorial icons.
- **Icons8 URL pattern:** `https://img.icons8.com/ios/{size}/{hex}/{icon-name}.png` — e.g. `https://img.icons8.com/ios/100/872D2E/shield.png` for Build Canada red at 100px source size. Verify each URL returns a valid image before shipping.
- **Colour:** Default charcoal `#2A2A2A` for table and section icons. Build Canada red `#872D2E` is acceptable for accent icons on cards, carousels, or emphasis rows when the layout calls for brand colour.
- **Placement:** Left-aligned in the icon/label column when using a table, or beside a section heading or list title when using another layout. On card rows, icons may sit on the right. Keep icons aligned consistently within the piece.
- **Topics mapped to icons:** Use intuitive government/finance/civic metaphors — coins/database for funding, globe for international, scales for governance, people for citizens, shield/check for safeguards.
- **Consistency:** Use one icon family per graphic, keep stroke/visual weight consistent, and size all icons uniformly within a given layout zone.
- **Do not use:** Hand-drawn inline SVG pictorial icons, mixed icon families, emoji-as-icons, or decorative illustrations.

---

## Tone & Content Principles

- **Analytical, not promotional.** Headlines should state a clear editorial position or finding (e.g. "A sovereign wealth fund in name only"), not a marketing tagline.
- **Comparisons when they help.** Side-by-side layouts work well when contrasting two positions, proposals, or options (often official or government versus aspirational or alternative). They are **not** required for every graphic. Lists, single-track narratives, and chart-led pieces are equally valid when they carry the argument more clearly.
- **Data first.** Lead each row, list item, or section with the most concrete number or fact available. Avoid vague descriptors.
- **Concise blocks.** Each table cell or list item should contain about 1–3 short sentences maximum. Dense but not cluttered.
- **Semicolons (on-canvas copy):** Do **not** use semicolons (`;`) in text rendered inside the graphic (hero, deck, stat callouts, table cells, themes, calendar chips, footer). Break lists and related clauses with **commas**, and separate distinct statements with **periods**.
- **Em dash and en dash (on-canvas copy):** Do **not** use **em dashes** (`—`, U+2014) or **en dashes** (`–`, U+2013) in infographic body copy, labels, captions, or footers. Use the **ASCII hyphen-minus** (`-`) for numeric and fiscal ranges (e.g. `2025-2026`, `80-100k`). Where prose would normally take an em-dash break, use a **comma**, **period**, or **spaced hyphen** (` - `) instead.
- **Source attribution always.** Every graphic must include a source line at the bottom citing specific documents, organisations, and dates — **plain text only**, no hyperlinks on-canvas (see **Caption / source text**).
- **No meta disclaimers on-canvas.** Do not add editorial housekeeping lines to the graphic footer (e.g. “Summary only”, “verify eligibility”, “not investment advice”). Attribution stays factual; qualifiers belong outside the artwork if needed.
- **Neutral framing of data, pointed framing of headlines.** The body copy presents facts; the headline is allowed to carry an editorial judgment.
- **Reference recreation fidelity:** When recreating a supplied image, preserve the source image's visible copy, labels, and data framing unless the user explicitly asks for rewrites. Do not invent replacement editorial copy or add new claims just because they fit the layout.
- **Data substitution only where requested:** If the user provides a CSV or other data source for a chart/map, use that data for the chart/map while keeping non-chart copy faithful to the supplied reference image.
- **Exact requested copy:** When the user supplies wording to add, preserve it exactly except for clearly necessary typographic escaping in HTML. Do not paraphrase user-supplied sentences.
- **Avoid duplicate callout labels:** If a callout already has a large heading such as "TL;DR", do not also include a small duplicate label above it unless the reference image clearly requires both.

---

## Brand Mark

- **File:** The official Build Canada logo is available as a PNG in the directory. Always use this file rather than recreating the mark.
- **Position:** Top right corner of the canvas.
- **Form (asset):** The PNG is the full mark — central Build Canada red (`#872D2E`) square with white “Build” / “Canada” text, with any narrow rose-taupe side bars **baked into the image**. Do not approximate the mark in HTML.
- **HTML `.brand` wrapper — no halo:** Set the logo container’s background to the **same parchment as the canvas** (`#F4EBE3` / `var(--paper)`), not `#C4A090`. Do **not** add a border, outline, or drop shadow on the wrapper. Painting a second taupe tile behind the PNG stacks against semi-transparent edge pixels and reads as a muddy fringe or **halo** beside the built-in side bars. Use `object-fit: contain` (not `cover`) so the full mark scales cleanly inside the reserved box.
- **Size:** Approximately 60×50px to 72×72px at standard canvas size — compact, not dominant; keep proportions consistent within a given graphic.
- **Do not:** Stretch, recolour, crop the mark with `object-fit: cover`, or add drop shadows or coloured boxes outside what the PNG already provides.

---

## Do's and Don'ts

| Do | Don't |
|---|---|
| Use the warm cream background | Use pure white or cool grey backgrounds |
| Use brick red and teal as the two accent colours | Introduce additional accent colours |
| Use online icon library assets (Icons8, etc.) | Hand-draw inline SVG pictorial icons |
| Keep icons monochrome or brand red per brief | Mix icon families or use emoji as icons |
| Set data figures in oversized bold type with slight positive letter-spacing | Bury key numbers in body copy or clamp them with heavy negative tracking |
| State a clear editorial headline | Write a vague or neutral headline |
| Pick layout (table, list, chart, map, stack) by what the story needs | Default every graphic to a comparison table out of habit |
| Keep header kicker, H1, and deck **substantially larger** than body copy (see Typography — Header zone type scale) | Shrink header fonts to cram denser body content |
| Keep body, labels, stats, and footer large enough for phones/feeds (see Typography — Cross-platform legibility) | Use uniformly tiny type across the canvas to fit more words |
| Design chart-heavy graphics so axis labels, legends, and data callouts read on a phone at full width without pinch-zoom | Cram multiple charts with footnote-sized axis text to fit everything on one canvas |
| Use commas and periods in canvas copy, not semicolons (see Tone — punctuation) | Use semicolons to chain clauses or lists on the graphic |
| Use ASCII `-` for ranges and dash-like breaks per Tone rules | Use em dashes or en dashes in on-canvas copy |
| Cite sources as plain text on the canvas (title, organisation, date) | Use hyperlinks, underlined URLs, or `<a>` tags in the graphic footer |
| Attribute all sources with dates | Omit source lines |
| Use a black `#1A1A1A` inset canvas frame (see Layout — Border) | Use brand red for the default outer canvas outline |
| Maintain generous outer margins | Crowd content to the edges |
| Match the warm parchment tone across all elements | Mix cool and warm tones in the same graphic |
| Preserve supplied reference copy when recreating an image | Inject new editorial copy without being asked |
| Check the rendered HTML for clipping before finalizing | Hand off an HTML file with content falling off the canvas |
| Use the local iOS Emoji Flags PNG assets for flags | Draw approximate flags manually or use native emoji glyphs |
| Keep map legends close to integrated parchment maps | Leave a large empty gap between a map and its legend |
| Use established funding-model colours consistently | Swap semantic colours without updating map, legend, and notes together |
| Pin hero-and-body teaser sources to the bottom of the body column (see Layout — Hero-and-body teaser) | Let attribution float directly under short copy mid-canvas |
| Pixel-scan crop publisher logos and use equal CSS padding on hero badges (see Layout — Publisher badge) | Compensate for logo whitespace with scale transforms or overflow clip boxes |
| Put PNG download controls below and outside the canvas | Include export controls inside the exported graphic |

---

*This guide is intended as a prompt-ready reference for AI image generation, design systems, and layout tools working within the Build Canada visual identity.*