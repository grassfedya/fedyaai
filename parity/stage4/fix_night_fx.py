#!/usr/bin/env python3
"""Rebuild night_fx: smoke = large connected residual components only;
staff = clean hand geometry (shaft + hooked head) colored from the variant."""
import cv2, json, sys
import numpy as np
sys.path.insert(0, "/private/tmp/claude-501/-Users-fedyamuzyka-projects-fedyaai/4b787d10-4dcc-41bf-b959-e1ec00fcbc8a/scratchpad")
from sample_variants import load_rgb, lum, rgb2hex, ROOT, SP, W, H

var = load_rgb(f"{ROOT}/public/images/Night.png")
ren = load_rgb(f"{SP}/render_night.png")
nres = lum(var) - lum(ren)

def trace(m, min_area=20, eps=1.0):
    cnts, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    for c in cnts:
        if cv2.contourArea(c) < min_area: continue
        c = cv2.approxPolyDP(c, eps, True)[:, 0, :]
        if len(c) < 3: continue
        out.append("M" + " ".join(f"{p[0]},{p[1]}" for p in c) + "Z")
    return out

box = np.zeros((H, W), bool); box[635:800, 1530:1700] = True
smoke = (nres > 10) & box
smoke = cv2.morphologyEx(smoke.astype(np.uint8), cv2.MORPH_CLOSE,
                         cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5)))
n, lab, stats, _ = cv2.connectedComponentsWithStats(smoke, 8)
keep = np.zeros((H, W), bool)
for i in range(1, n):
    if stats[i, cv2.CC_STAT_AREA] >= 150:
        keep |= (lab == i)
print("smoke kept px:", keep.sum(), "of", (smoke > 0).sum())
spx = var[keep]
Ls = lum(spx)
med = np.median(Ls)
hi = np.zeros((H, W), bool); hi[keep] = Ls > med
lo = keep & ~hi
nfx = []
for m, op in [(lo, 0.5), (hi, 0.85)]:
    if m.sum() < 40: continue
    col = rgb2hex(tuple(np.median(var[m][:, i]) for i in range(3)))
    d = trace(m, 30, 1.0)
    if d: nfx.append(f'<path fill="{col}" fill-opacity="{op}" d="{"".join(d)}"/>')

# staff: shaft from grip to head, slight lean; hooked blade at top
sbox = var[655:790, 1800:1845]
scol = rgb2hex(tuple(np.percentile(sbox.reshape(-1,3)[:, i], 20) for i in range(3)))
shaft = "M1811,784 L1815,784 L1829,671 L1824,669 Z"
head = ("M1826,673 C1822,660 1828,650 1838,647 C1833,655 1833,662 1836,668 "
        "C1833,672 1829,674 1826,673 Z")
nub = '<circle cx="1838" cy="647" r="2.6"/>'
nfx.append(f'<g fill="{scol}"><path d="{shaft}"/><path d="{head}"/>{nub}</g>')
print("staff color:", scol)

ov = json.load(open(f"{SP}/overlays.json"))
ov["night_fx"] = "".join(nfx)
json.dump(ov, open(f"{SP}/overlays.json", "w"))
print("night_fx bytes:", len(ov["night_fx"]))
