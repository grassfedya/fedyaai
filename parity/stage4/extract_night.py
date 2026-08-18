#!/usr/bin/env python3
"""Extract starfield + moon (disc, craters, glow) from Night.png into overlays.json."""
import cv2, json, sys
import numpy as np
sys.path.insert(0, "/private/tmp/claude-501/-Users-fedyamuzyka-projects-fedyaai/4b787d10-4dcc-41bf-b959-e1ec00fcbc8a/scratchpad")
from sample_variants import load_rgb, lum, rgb2hex, ROOT, SP, W, H

night = load_rgb(f"{ROOT}/public/images/Night.png")
sky = cv2.imread(f"{ROOT}/parity/masks/sky.png", cv2.IMREAD_GRAYSCALE) > 127
L = lum(night)

# ---- moon: disc extent at a generous threshold near the known bright blob
seed = None
cand = (L > 170)
n, lab, stats, cent = cv2.connectedComponentsWithStats(cand.astype(np.uint8), 8)
i = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
mcx, mcy = cent[i]
yy, xx = np.mgrid[0:H, 0:W]
d = np.sqrt((xx - mcx)**2 + (yy - mcy)**2)
# disc = contiguous region L>110 within 120px of centroid
disc = (L > 110) & (d < 120)
n2, lab2, st2, ct2 = cv2.connectedComponentsWithStats(disc.astype(np.uint8), 8)
i2 = 1 + np.argmax(st2[1:, cv2.CC_STAT_AREA])
area = st2[i2, cv2.CC_STAT_AREA]
mcx, mcy = ct2[i2]
mr = float(np.sqrt(area / np.pi))
d = np.sqrt((xx - mcx)**2 + (yy - mcy)**2)
disc_m = (lab2 == i2)
disc_px = night[disc_m]
disc_col = rgb2hex(tuple(np.percentile(disc_px[:, i], 75) for i in range(3)))
disc_med_L = np.median(lum(disc_px))

# craters: darker patches inside disc
crat = disc_m & (L < disc_med_L - 8)
crat = cv2.morphologyEx(crat.astype(np.uint8), cv2.MORPH_OPEN,
                        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
crat_col = rgb2hex(tuple(np.median(night[crat > 0][:, i]) for i in range(3))) if crat.sum() > 30 else None
cnts, _ = cv2.findContours(crat, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
crater_paths = []
for c in cnts:
    if cv2.contourArea(c) < 12: continue
    c = cv2.approxPolyDP(c, 1.2, True)[:, 0, :]
    pth = "M" + " ".join(f"{p[0]},{p[1]}" for p in c) + "Z"
    crater_paths.append(pth)

# glow radial profile: median L in annuli vs far sky
far = np.median(L[(d > mr*8) & sky])
prof = []
for k in (1.15, 1.5, 2.0, 2.8, 3.8, 5.0, 6.5):
    ring = (d > mr*(k-0.12)) & (d < mr*(k+0.12)) & sky & ~disc_m
    if ring.sum() < 50: continue
    med = np.median(L[ring])
    prof.append((k, max(0.0, (med - far))))
peak = prof[0][1] if prof else 40.0
stops = [(0.0, 1.0), (float(mr/ (mr*7)), 1.0)]
glow_stops = ""
R = mr * 7
glow_col = "#cfe0f4"
glow_stops += f'<stop offset="0" stop-color="{glow_col}" stop-opacity="0.9"/>'
for k, dl in prof:
    op = round(min(0.9, dl / 255 * 2.6), 3)
    glow_stops += f'<stop offset="{round(k*mr/R,4)}" stop-color="{glow_col}" stop-opacity="{op}"/>'
glow_stops += f'<stop offset="1" stop-color="{glow_col}" stop-opacity="0"/>'

moon_svg = (
    f'<defs><radialGradient id="moon-glow" gradientUnits="userSpaceOnUse" cx="{mcx:.0f}" cy="{mcy:.0f}" r="{R:.0f}">'
    f'{glow_stops}</radialGradient>'
    f'<clipPath id="moon-clip"><circle cx="{mcx:.0f}" cy="{mcy:.0f}" r="{mr:.1f}"/></clipPath></defs>'
    f'<circle cx="{mcx:.0f}" cy="{mcy:.0f}" r="{R:.0f}" fill="url(#moon-glow)"/>'
    f'<circle cx="{mcx:.0f}" cy="{mcy:.0f}" r="{mr:.1f}" fill="{disc_col}"/>'
)
if crater_paths and crat_col:
    moon_svg += f'<g clip-path="url(#moon-clip)" fill="{crat_col}" opacity="0.85">'
    moon_svg += "".join(f'<path d="{p}"/>' for p in crater_paths)
    moon_svg += "</g>"

print(f"moon: c=({mcx:.0f},{mcy:.0f}) r={mr:.1f} disc={disc_col} craters={len(crater_paths)} {crat_col}")
print("glow profile:", [(k, round(v,1)) for k, v in prof])

# ---- stars: bright small blobs vs row background, outside moon glow core
rowbg = np.array([np.median(L[y][sky[y]]) if sky[y].sum() > 200 else 255 for y in range(H)])
starm = sky & (L > rowbg[:, None] + 22) & (d > mr * 2.2)
n3, lab3, st3, ct3 = cv2.connectedComponentsWithStats(starm.astype(np.uint8), 8)
stars = []
for i in range(1, n3):
    a = st3[i, cv2.CC_STAT_AREA]
    if a < 2 or a > 120: continue
    cx, cy = ct3[i]
    peakL = L[lab3 == i].max()
    stars.append((cx, cy, a, peakL))
print("stars:", len(stars))
star_parts = []
big = 0
for cx, cy, a, pk in stars:
    r = max(0.7, min(2.6, np.sqrt(a / np.pi)))
    op = round(min(1.0, 0.35 + (pk - 60) / 200), 2)
    star_parts.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.1f}" opacity="{op}"/>')
    if a >= 28:  # flare cross on the brightest
        fl = min(11, a / 4)
        star_parts.append(f'<path d="M{cx:.0f} {cy-fl:.0f}L{cx:.0f} {cy+fl:.0f}M{cx-fl:.0f} {cy:.0f}L{cx+fl:.0f} {cy:.0f}" stroke="#dfe9f5" stroke-width="0.9" opacity="{op*0.7:.2f}" fill="none"/>')
        big += 1
print("flared:", big)
stars_svg = f'<g fill="#dfe9f5">{"".join(star_parts)}</g>'

try:
    ov = json.load(open(f"{SP}/overlays.json"))
except FileNotFoundError:
    ov = {}
ov["stars"] = stars_svg
ov["moon"] = moon_svg
json.dump(ov, open(f"{SP}/overlays.json", "w"))
print("overlays.json written:", {k: len(v) for k, v in ov.items()})
