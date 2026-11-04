#!/usr/bin/env python3
"""Side by side: fish 0 from the real page's code, the sprite-mode copy in the same pose, and a pet frame, all at 1:1 px."""
import base64, html, io, json, re, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw

HERE = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
WATER = (13, 19, 21, 255)


def grab(query):
    with tempfile.TemporaryDirectory() as prof:
        r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={prof}",
                            "--allow-file-access-from-files", "--virtual-time-budget=15000", "--dump-dom",
                            (HERE / "compare.html").as_uri() + "?" + query], capture_output=True, text=True, timeout=120)
    dom = r.stdout
    meta = html.unescape(re.search(r'<pre id="meta">(.*?)</pre>', dom, re.S).group(1))
    if meta.startswith("ERROR"):
        sys.exit(meta)
    img = lambda k: Image.open(io.BytesIO(base64.b64decode(re.search(rf'<pre id="{k}">data:image/png;base64,(.*?)</pre>', dom, re.S).group(1)))).convert("RGBA")
    return json.loads(meta), img("page"), img("sprite")


t = sys.argv[1] if len(sys.argv) > 1 else "7"
atlas, out = Path(sys.argv[2]), Path(sys.argv[3])
meta, page, glint = grab(f"t={t}&glint=1")
_, _, plain = grab(f"t={t}&glint=0")
print(json.dumps(meta))
on_water = lambda im: (lambda b: (b.alpha_composite(im), b)[1])(Image.new("RGBA", im.size, WATER))
g, p = on_water(glint), on_water(plain)
# where the sprite copy differs from the page: only the water around the koi should light up (shade, caustics, other koi, wake)
diff = ImageChops.difference(page.convert("RGB"), g.convert("RGB")).point(lambda v: 255 if v > 6 else 0).convert("RGB")
koi_mask = glint.getchannel("A").point(lambda v: 255 if v > 0 else 0)
inside = ImageChops.multiply(diff.convert("L"), koi_mask)
changed_inside = sum(1 for v in inside.getdata() if v)
print("koi pixels:", sum(1 for v in koi_mask.getdata() if v), " differing koi pixels (sprite+glint vs page):", changed_inside)
pet = Image.open(atlas).convert("RGBA").crop((0, 0, 192, 208))
pet = on_water(pet)
panels = [("page code (pond.js, unmodified)", page), ("sprite copy, same pose, glints on", g),
          ("sprite copy, same pose, glints off", p), ("pet idle frame 0 (K 0.84)", pet), ("diff page vs glints-on", diff.convert("RGBA"))]
Wd = sum(im.width for _, im in panels) + 12 * (len(panels) + 1)
Hd = max(im.height for _, im in panels) + 40
sheet = Image.new("RGB", (Wd, Hd), (60, 60, 60))
d = ImageDraw.Draw(sheet)
x = 12
for label, im in panels:
    sheet.paste(im.convert("RGB"), (x, 30))
    d.text((x, 8), label, fill=(240, 240, 240))
    x += im.width + 12
sheet.save(out)
print(out)
