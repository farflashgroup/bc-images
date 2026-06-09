"""Apply Build Canada photo bezels: parchment mat, inset ink frame, red corner brackets."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

PAPER = (244, 235, 227)
INK = (26, 26, 26)
RED = (135, 45, 46)

FRAME_INSET = 10
BORDER_W = 1
MAT_RATIO = 0.012
MAT_MIN = 8
CORNER_RATIO = 0.089
CORNER_THICK_RATIO = 0.0056


def apply_bezel(source: Path, dest: Path) -> None:
    photo = Image.open(source).convert("RGB")
    pw, ph = photo.size

    mat = max(MAT_MIN, round(pw * MAT_RATIO))
    inner_w = pw + 2 * mat
    inner_h = ph + 2 * mat
    canvas_w = inner_w + 2 * (FRAME_INSET + BORDER_W)
    canvas_h = inner_h + 2 * (FRAME_INSET + BORDER_W)

    canvas = Image.new("RGB", (canvas_w, canvas_h), PAPER)
    photo_x = FRAME_INSET + BORDER_W + mat
    photo_y = FRAME_INSET + BORDER_W + mat
    canvas.paste(photo, (photo_x, photo_y))

    draw = ImageDraw.Draw(canvas)
    frame_left = FRAME_INSET
    frame_top = FRAME_INSET
    frame_right = canvas_w - FRAME_INSET - 1
    frame_bottom = canvas_h - FRAME_INSET - 1

    for i in range(BORDER_W):
        draw.rectangle(
            (
                frame_left + i,
                frame_top + i,
                frame_right - i,
                frame_bottom - i,
            ),
            outline=INK,
        )

    corner_len = max(48, round(canvas_w * CORNER_RATIO))
    corner_thick = max(3, round(canvas_w * CORNER_THICK_RATIO))

    def corner_tl(x: int, y: int) -> None:
        draw.rectangle((x, y, x + corner_len, y + corner_thick), fill=RED)
        draw.rectangle((x, y, x + corner_thick, y + corner_len), fill=RED)

    def corner_br(x: int, y: int) -> None:
        draw.rectangle((x - corner_len + 1, y, x + 1, y + corner_thick), fill=RED)
        draw.rectangle((x - corner_thick + 1, y - corner_len + 1, x + 1, y + 1), fill=RED)

    corner_tl(frame_left, frame_top)
    corner_br(frame_right, frame_bottom)

    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, format="PNG", optimize=True)


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit("Usage: _apply-photo-bezel.py <source> <dest>")

    apply_bezel(Path(sys.argv[1]), Path(sys.argv[2]))


if __name__ == "__main__":
    main()
