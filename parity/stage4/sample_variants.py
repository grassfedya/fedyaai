#!/usr/bin/env python3
"""Stage 4: sample Day/Dusk/Night variants into per-region token sets.

Method: for each region, rank reference pixels (eroded mask) by luminance.
Each dawn token color gets a luminance quantile q in that distribution; its
variant value is the per-channel median of the variant's mask pixels in the
band q +/- BAND of the variant's own luminance ranking. Ordering-preserving,
handles nonlinear compression (night) better than mean/std affine transfer.
"""
import cv2, json, os, re, sys
import numpy as np

ROOT = "/Users/fedyamuzyka/projects/fedyaai"
SP = os.path.dirname(os.path.abspath(__file__))  # parity/stage4: inputs and outputs live here
W, H = 2028, 1108
BAND = 0.03
ERODE_R = 12
MIN_PX = 500

REGIONS = ["sky","far_ridges","mountain_rock","snow_cap","crevasses","mid_ridges",
           "green_hills","terraces","river","foreground_forest","sun_disc","sun_ring","pipe_smoke"]

def load_rgb(path, resize=True):
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if im.shape[2] == 4:
        im = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)
    if resize and (im.shape[1], im.shape[0]) != (W, H):
        im = cv2.resize(im, (W, H), interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

def lum(px):  # px: (...,3) float or uint8 RGB
    px = px.astype(np.float64)
    return 0.299*px[...,0] + 0.587*px[...,1] + 0.114*px[...,2]

def eroded_mask(name):
    m = cv2.imread(f"{ROOT}/parity/masks/{name}.png", cv2.IMREAD_GRAYSCALE)
    r = ERODE_R
    while r > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*r+1, 2*r+1))
        e = cv2.erode(m, k)
        if (e > 127).sum() >= MIN_PX:
            return e > 127
        r -= 2
    return m > 127

def region_pixels(img, mask):
    return img[mask]

def hex2rgb(h):
    h = h.lstrip('#')
    if len(h) == 3: h = ''.join(c*2 for c in h)
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb2hex(c):
    return '#%02x%02x%02x' % tuple(int(round(min(255, max(0, v)))) for v in c)

def build_transfer(ref_px, var_px):
    """Return f(rgb)->rgb by luminance-quantile matching."""
    rl = np.sort(lum(ref_px))
    vl = lum(var_px)
    order = np.argsort(vl)
    var_sorted = var_px[order]
    n = len(var_sorted)
    def f(rgb):
        q = np.searchsorted(rl, lum(np.array([rgb]))[0]) / max(1, len(rl))
        lo, hi = int(max(0, (q-BAND)*n)), int(min(n, (q+BAND)*n))
        if hi <= lo: lo, hi = max(0, min(n-1, int(q*n))), max(1, min(n, int(q*n)+1))
        band = var_sorted[lo:hi]
        return tuple(np.median(band[:, i]) for i in range(3))
    return f

def group_colors(svg, name):
    start = svg.index(f'<g id="{name}"')
    depth = 0
    for mm in re.finditer(r'<g[ >]|</g>', svg[start:]):
        depth += 1 if not mm.group(0).startswith('</') else -1
        if depth == 0:
            seg = svg[start:start+mm.end()]
            break
    cols = set(re.findall(r'(?:fill|stroke|stop-color)="(#[0-9a-fA-F]+)"', seg))
    return {c.lower() for c in cols} - {'#ffffff', '#000000'} if name == 'sun_ring' else {c.lower() for c in cols}

def lab_of(hexcol):
    arr = np.uint8([[hex2rgb(hexcol)]])
    return cv2.cvtColor(arr, cv2.COLOR_RGB2LAB)[0, 0].astype(np.float64)

def bright_blob(img, mask, thresh):
    L = lum(img)
    cand = (L > thresh) & mask
    n, lab, stats, cent = cv2.connectedComponentsWithStats(cand.astype(np.uint8), 8)
    if n <= 1: return None
    i = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    area = stats[i, cv2.CC_STAT_AREA]
    cx, cy = cent[i]
    return dict(cx=float(cx), cy=float(cy), r=float(np.sqrt(area/np.pi)), area=int(area))

def main():
    svg = open(f"{SP}/working.svg").read()
    ref = load_rgb(f"{ROOT}/public/images/reference_bg.png")
    variants = {v: load_rgb(f"{ROOT}/public/images/{v}.png") for v in ["Day", "Dusk", "Night"]}
    masks = {r: eroded_mask(r) for r in REGIONS}
    sky_full = cv2.imread(f"{ROOT}/parity/masks/sky.png", cv2.IMREAD_GRAYSCALE) > 127

    # global transfer source: union of all masks
    union = np.zeros((H, W), bool)
    for m in masks.values(): union |= m

    out = {"tokens": {}, "sky_base_rows": {}, "specials": {}}

    # per-region transfers
    transfers = {}
    for v, img in variants.items():
        transfers[v] = {}
        for r in REGIONS:
            rp, vp = ref[masks[r]], img[masks[r]]
            if len(rp) < 50:
                continue
            transfers[v][r] = build_transfer(rp, vp)
        transfers[v]["__global__"] = build_transfer(ref[union], img[union])

    # region group colors
    region_palettes = {}
    for r in REGIONS:
        try:
            region_palettes[r] = sorted(group_colors(svg, r))
        except ValueError:
            region_palettes[r] = []
    # river gradient stops live inside river group already (stop-color caught)

    for r in REGIONS:
        for c in region_palettes[r]:
            key = f"{r}:{c}"
            out["tokens"][key] = {}
            for v in variants:
                f = transfers[v].get(r) or transfers[v]["__global__"]
                out["tokens"][key][v] = rgb2hex(f(hex2rgb(c)))

    # underpaint + birds: nearest dawn color across region palettes (Lab)
    cand = [(r, c, lab_of(c)) for r in REGIONS for c in region_palettes[r]
            if r not in ("sun_disc", "sun_ring")]
    for gname in ["underpaint", "birds"]:
        cols = sorted(group_colors(svg, gname))
        for c in cols:
            lab = lab_of(c)
            r_best, c_best = min(((rr, cc) for rr, cc, ll in cand),
                                 key=lambda t: np.sum((lab_of(t[1]) - lab)**2))
            key = f"{gname}:{c}"
            out["tokens"][key] = {}
            for v in variants:
                f = transfers[v].get(r_best) or transfers[v]["__global__"]
                out["tokens"][key][v] = rgb2hex(f(hex2rgb(c)))
            out["tokens"][key]["via"] = f"{r_best}:{c_best}"

    # sky-base stops: sample variant sky rows at each stop's y
    stops = [0.0, 0.0361, 0.0812, 0.1354, 0.1895, 0.2437, 0.2978, 0.3520, 0.4061, 0.4792, 1.0]
    for v, img in variants.items():
        rows = []
        last = None
        for off in stops:
            y = min(H-1, int(round(off*H)))
            got = None
            for dy in range(0, 60):
                for yy in (y-dy, y+dy):
                    if 0 <= yy < H and sky_full[yy].sum() > 200:
                        px = img[yy][sky_full[yy]]
                        got = rgb2hex(tuple(np.median(px[:, i]) for i in range(3)))
                        break
                if got: break
            rows.append(got or last or "#000000")
            last = rows[-1]
        out["sky_base_rows"][v] = dict(zip(map(str, stops), rows))

    # luminaries
    sp = {}
    day = variants["Day"]
    sp["day_sun"] = bright_blob(day, sky_full, 245)
    if sp["day_sun"]:
        cx, cy, r = sp["day_sun"]["cx"], sp["day_sun"]["cy"], sp["day_sun"]["r"]
        yy, xx = np.mgrid[0:H, 0:W]
        d = np.sqrt((xx-cx)**2 + (yy-cy)**2)
        core = day[(d < r*0.6)]
        ring = day[(d > r*1.1) & (d < r*1.6)]
        halo = day[(d > r*2.5) & (d < r*4.0) & sky_full]
        sp["day_sun"]["core"] = rgb2hex(tuple(np.median(core[:, i]) for i in range(3)))
        sp["day_sun"]["ring"] = rgb2hex(tuple(np.median(ring[:, i]) for i in range(3)))
        sp["day_sun"]["halo"] = rgb2hex(tuple(np.median(halo[:, i]) for i in range(3)))
    night = variants["Night"]
    sp["night_moon"] = bright_blob(night, np.ones((H, W), bool), 170)
    if sp["night_moon"]:
        cx, cy, r = (sp["night_moon"][k] for k in ("cx", "cy", "r"))
        yy, xx = np.mgrid[0:H, 0:W]
        d = np.sqrt((xx-cx)**2 + (yy-cy)**2)
        sp["night_moon"]["core"] = rgb2hex(tuple(np.median(night[d < r*0.5][:, i]) for i in range(3)))
        sp["night_moon"]["glow"] = rgb2hex(tuple(np.median(night[(d > r*1.5) & (d < r*2.5)][:, i]) for i in range(3)))
        sp["night_moon"]["sky_far"] = rgb2hex(tuple(np.median(night[(d > r*6) & sky_full][:, i]) for i in range(3)))
    dusk = variants["Dusk"]
    Ld = lum(dusk)
    right = np.zeros((H, W), bool); right[:, int(W*0.6):] = True
    sp["dusk_glow"] = bright_blob(dusk, right, 200)
    # dusk sky brightest row on the right edge for glow seat
    json.dump(out | {"specials": sp}, open(f"{SP}/tokens.json", "w"), indent=1)
    print("tokens:", len(out["tokens"]))
    print("specials:", json.dumps(sp, indent=1))

if __name__ == "__main__":
    main()
