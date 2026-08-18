#!/usr/bin/env python3
"""Dusk pass 3, phased. --phase sky: fit the per-column horizontal sky layer
against the current render. --phase rim: fit two-sided mountain correction +
front glow against the current render. Run with regen+rerender between."""
import cv2, json, sys
import numpy as np
sys.path.insert(0, "/private/tmp/claude-501/-Users-fedyamuzyka-projects-fedyaai/4b787d10-4dcc-41bf-b959-e1ec00fcbc8a/scratchpad")
from sample_variants import load_rgb, lum, hex2rgb, rgb2hex, ROOT, SP, W, H

phase = sys.argv[1]
mask = lambda n: cv2.imread(f"{ROOT}/parity/masks/{n}.png", cv2.IMREAD_GRAYSCALE) > 127
sky = mask("sky")
var = load_rgb(f"{ROOT}/public/images/Dusk.png")
ren = load_rgb(f"{SP}/render_dusk.png")
resid = lum(var) - lum(ren)
overlays = json.load(open(f"{SP}/overlays.json"))

if phase == "sky":
    xs = list(range(0, 2029, 156))  # 14 stops, fixed upper band so every column samples the same rows
    Y0, Y1 = 120, 320
    stops = []
    for x in xs:
        x0, x1 = max(0, x-90), min(W, x+90)
        m = sky[Y0:Y1, x0:x1].copy()
        if m.sum() < 300:
            stops.append((x/2028, "#000000", 0.0)); continue
        vcol = tuple(np.median(var[Y0:Y1, x0:x1][m][:, i]) for i in range(3))
        rL = float(np.median(lum(ren[Y0:Y1, x0:x1][m])))
        mag = float(np.abs(np.median(resid[Y0:Y1, x0:x1][m])))
        dl = abs(lum(np.array(vcol)) - rL)
        a = min(0.65, mag / max(10.0, dl))
        if mag < 4: a = 0.0
        stops.append((round(x/2028, 4), rgb2hex(vcol), round(a, 3)))
    grad = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
    # right glow at sky level, fitted on sky pixels
    yy, xx = np.mgrid[0:H, 0:W]
    gx, gy, R = 1817, 489, 420
    gcol = "#ffc98a"; gL = lum(np.array(hex2rgb(gcol)))
    d2 = np.sqrt((xx-gx)**2 + (yy-gy)**2)
    gstops = []
    for r in [25, 70, 130, 200, 280, 370]:
        ring = (np.abs(d2 - r) < 18) & sky
        if ring.sum() < 40:
            gstops.append((round(r/R, 3), 0.35)); continue
        need = max(0.0, float(np.median(resid[ring])))
        have = float(np.median(lum(ren[ring])))
        a = min(0.9, need / max(1.0, gL - have))
        gstops.append((round(r/R, 3), round(a, 3)))
    gstops.append((1.0, 0.0))
    ggrad = "".join(f'<stop offset="{o}" stop-color="{gcol}" stop-opacity="{a}"/>' for o, a in gstops)
    overlays["dusk_sky_lr"] = (
        f'<defs><linearGradient id="dsl-g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="2028" y2="0">{grad}</linearGradient>'
        f'<radialGradient id="dsl-glow" gradientUnits="userSpaceOnUse" cx="{gx}" cy="{gy}" r="{R}">{ggrad}</radialGradient></defs>'
        f'<rect x="0" y="0" width="2028" height="1108" fill="url(#dsl-g)"/>'
        f'<circle cx="{gx}" cy="{gy}" r="{R}" fill="url(#dsl-glow)"/>'
    )
    print("sky lr stops:", stops)
    print("sky glow stops:", gstops)

elif phase == "rim":
    yy, xx = np.mgrid[0:H, 0:W]
    mtn = np.zeros((H, W), bool)
    for n in ["snow_cap","crevasses","mountain_rock","far_ridges","mid_ridges"]:
        mtn |= mask(n)

    def trace(m, min_area=30, eps=1.2):
        cnts, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        out = []
        for c in cnts:
            if cv2.contourArea(c) < min_area: continue
            c = cv2.approxPolyDP(c, eps, True)[:, 0, :]
            if len(c) < 3: continue
            out.append("M" + " ".join(f"{p[0]},{p[1]}" for p in c) + "Z")
        return out

    sel = (np.abs(resid) > 12) & mtn
    sel = cv2.morphologyEx(sel.astype(np.uint8), cv2.MORPH_OPEN,
                           cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))) > 0
    px = var[sel]
    print("rim/shade px:", sel.sum())
    parts = []
    if sel.sum() > 300:
        Z = cv2.cvtColor(px.reshape(-1,1,3).astype(np.uint8), cv2.COLOR_RGB2LAB).reshape(-1,3).astype(np.float32)
        K = 5
        _, lab_idx, ctr = cv2.kmeans(Z, K, None,
            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5), 3, cv2.KMEANS_PP_CENTERS)
        full = np.zeros((H, W), np.int8) - 1
        full[sel] = lab_idx.ravel()
        ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
        for k in range(K):
            m = (full == k).astype(np.uint8)
            if m.sum() < 60: continue
            col = rgb2hex(tuple(np.median(px[lab_idx.ravel() == k][:, i]) for i in range(3)))
            inner = cv2.erode(m, ker)
            band = (m > 0) & (inner == 0)
            d_in = trace(inner, 25)
            d_bd = trace(band.astype(np.uint8), 25)
            if d_bd:
                parts.append(f'<path fill="{col}" fill-opacity="0.45" d="{"".join(d_bd)}"/>')
            if d_in:
                parts.append(f'<path fill="{col}" fill-opacity="0.92" d="{"".join(d_in)}"/>')
    overlays["dusk_rim"] = "".join(parts)
    glow_col = "#ffc98a"
    overlays["dusk_front"] = (
        f'<defs><radialGradient id="df-glow" gradientUnits="userSpaceOnUse" cx="1817" cy="489" r="420">'
        f'<stop offset="0" stop-color="{glow_col}" stop-opacity="0.28"/>'
        f'<stop offset="0.5" stop-color="{glow_col}" stop-opacity="0.10"/>'
        f'<stop offset="1" stop-color="{glow_col}" stop-opacity="0"/></radialGradient></defs>'
        f'<circle cx="1817" cy="489" r="420" fill="url(#df-glow)"/>'
    )

json.dump(overlays, open(f"{SP}/overlays.json", "w"))
print("overlays:", {k: len(v) for k, v in overlays.items()})
