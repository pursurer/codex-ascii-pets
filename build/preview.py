#!/usr/bin/env python3
"""README preview: both pets side by side on the black water, cycling idle, running-right, waving and jumping."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
W, H, WATER = 192, 208, (13, 19, 21)
# row index, frame durations (ms): the same timing as the Codex pet rows (qa.py)
ROWS = [(0, [280, 110, 110, 140, 140, 320]), (1, [120] * 7 + [220]), (3, [140] * 3 + [280]), (4, [140] * 4 + [280])]
pets = [Image.open(ROOT / "pets" / name / "spritesheet.webp").convert("RGBA") for name in ("ascii-koi", "ascii-cat")]

frames, durs = [], []
for row, row_durs in ROWS:
    for _ in range(2):  # each row plays twice
        for c, d in enumerate(row_durs):
            f = Image.new("RGBA", (2 * W + 48, H + 16), WATER + (255,))
            for i, atlas in enumerate(pets):
                f.alpha_composite(atlas.crop((c * W, row * H, c * W + W, row * H + H)), (16 + i * (W + 16), 8))
            frames.append(f.convert("RGB").quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
            durs.append(d)
out = ROOT / "media" / "preview.gif"
frames[0].save(out, save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=1, optimize=True)
print(out, out.stat().st_size // 1024, "KB")
