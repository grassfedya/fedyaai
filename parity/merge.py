#!/usr/bin/env python3
"""Stage 1 step 2: merge k=14 clusters into semantic region masks.

Each pixel gets exactly one semantic label. Rules are (cluster set) AND (spatial
gate), painted in priority order (first rule to claim a pixel wins). Leftover
pixels are absorbed by iterative dilation voting. Special regions (sun disc, sun
ring, birds) are extracted by color/scale, not clusters, and painted first.

Outputs: masks/<region>.png, overlay.png, contact_sheet.png, regions.json
"""

import json
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
REF = HERE.parent / "public/images/reference_bg.png"
W, H = 2028, 1108

bgr = cv2.imread(str(REF))
labels = np.load(HERE / "clusters_k14_index.npy")
UNSET = 255
sem = np.full((H, W), UNSET, np.uint8)

REGIONS = []  # (name, mask builder result) in paint priority order


def claim(name, mask):
    mask = mask & (sem == UNSET)
    sem[mask] = len(REGIONS)
    REGIONS.append(name)
    return mask


def in_clusters(*ids):
    return np.isin(labels, ids)


def zone(y0, y1, x0, x1):
    z = np.zeros((H, W), bool)
    z[y0:y1, x0:x1] = True
    return z


# ---- specials first -----------------------------------------------------------
# Sun disc: the painting's sun is a soft radial glow with no hard edge (radial
# probe: sat falls 70 -> 45 smoothly, steepest at r~103). The mask is the exact
# circle at the sat-55 crossing; stage 2 renders it as a radial gradient.
hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
yy, xx = np.mgrid[0:H, 0:W]
disc = (xx - 990) ** 2 + (yy - 195) ** 2 < 103 ** 2
claim("sun_disc", disc)

# Birds: dropped per Fedya (2026-08-16), to be re-added later. Their pixels fall
# to sky via the absorb pass; the sky tracer must ignore the dark specks.
# To restore: claim small dark components (area 8-900, clusters 1,2,8,10,11) in
# zone(150, 400, 400, 1650) & ~disc, painted before the ring so flock members
# inside the annulus stay birds.

# Sun ring: thin geometry in the annulus, found as deviation from smoothed sky.
# Sky clusters only, so the snow peak poking into the annulus stays out.
gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
ann = ((xx - 990) ** 2 + (yy - 195) ** 2 < 280 ** 2) & ~disc
smooth = cv2.medianBlur(bgr, 31).astype(np.int16)
dev = np.abs(bgr.astype(np.int16) - smooth).sum(axis=2)
ring = ann & (dev > 18) & in_clusters(0, 7, 9, 12) & ~((yy > 270) & (xx > 870) & (xx < 1110))
claim("sun_ring", ring)

# Pipe smoke: the wisp rising from the wizard's pipe. Color-wise it nearly
# matches the purple ridge band behind it, so it is found as deviation from the
# median-smoothed background (same trick as the ring), then filtered to
# components touching a hand-drawn spine corridor so band edges and pine tips
# stay out. Claimed before the ridges and forest so the x=1560 forest gate
# cannot cut it in half. wizard-bear.svg carries its own smoke group; stage 2
# decides whether the overlay's smoke or a traced path renders this region.
# Two detectors: the square-median dev above sees strands of any orientation but
# also band edges; a sliding row-median dev sees only vertical-ish anomalies and
# is blind to the horizontal ribbon and sweep strands. Max of both, gated to
# bluish pixels (trees and crag paths are green-dominant), clipped to tight
# corridors drawn along each visible strand.
sy0, sy1, sx0, sx1 = 600, 800, 1490, 1700
sub = bgr[sy0:sy1, sx0:sx1].astype(np.int16)
sh, sw_ = sub.shape[:2]
pad = np.pad(sub, ((0, 0), (35, 35), (0, 0)), mode="edge")
swin = np.lib.stride_tricks.sliding_window_view(pad, (71,), axis=1)
dev_h = np.abs(sub - np.median(swin, axis=-1)).sum(axis=2)
sdev = np.maximum(dev[sy0:sy1, sx0:sx1], dev_h)
bluish = (sub[:, :, 0] + 6) >= sub[:, :, 1]
STRANDS = [
    [(1668, 780), (1655, 765), (1640, 742), (1632, 725), (1626, 706),
     (1622, 690), (1612, 678), (1600, 670), (1580, 668), (1560, 660), (1549, 655)],
    [(1618, 728), (1590, 730), (1565, 732), (1553, 728)],
    [(1557, 672), (1575, 676), (1592, 678), (1605, 676)],
    [(1622, 700), (1638, 706), (1648, 712)],
]
cor = np.zeros((sh, sw_), np.uint8)
for s in STRANDS:
    pts = [(x - sx0, y - sy0) for x, y in s]
    for a, b in zip(pts, pts[1:]):
        cv2.line(cor, a, b, 1, 18)
sm = ((sdev > 17) & bluish & (cor > 0)).astype(np.uint8)
sm = cv2.morphologyEx(sm, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
sm = cv2.morphologyEx(sm, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
n, cc, stats, _ = cv2.connectedComponentsWithStats(sm, 8)
smoke = np.zeros((H, W), bool)
for i in range(1, n):
    if stats[i, cv2.CC_STAT_AREA] >= 20:
        smoke[sy0:sy1, sx0:sx1] |= cc == i
claim("pipe_smoke", smoke)

# ---- the mountain -------------------------------------------------------------
# Cap hull: bright snow (6) plus pale blue (7) inside the summit zone, hole-filled.
cap_zone = zone(270, 600, 600, 1400)
snowish = (in_clusters(6) | (in_clusters(7, 13) & cap_zone & (gray > 175))) & cap_zone
snow_u8 = cv2.morphologyEx(snowish.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((13, 13), np.uint8))
n, cc, stats, _ = cv2.connectedComponentsWithStats(snow_u8, 8)
cap_hull = np.zeros((H, W), np.uint8)
for i in range(1, n):
    if stats[i, cv2.CC_STAT_AREA] > 4000:
        cap_hull[cc == i] = 1
cap_hull = cv2.morphologyEx(cap_hull, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8)).astype(bool)
crevasses = cap_hull & in_clusters(1, 8, 13) & ~snowish
claim("crevasses", crevasses)
claim("snow_cap", cap_hull)

# Far ridges before rock, so the mauve layers keep their pixels. Mauve (13) only
# counts left and right of the mountain flanks; central 13 is base haze -> rock.
far = (in_clusters(13) & (zone(430, 680, 0, 700) | zone(430, 680, 1330, W))) \
    | (in_clusters(8, 12) & (zone(460, 615, 0, 640) | zone(460, 615, 1380, W)))
claim("far_ridges", far)

# Rock: mountain blues down through the base haze (central mauve 13 included).
# The bottom gate at y=705 sits inside a soft same-cluster gradient, so the flat
# line is invisible in paint.
rock = (in_clusters(1, 8) | (in_clusters(13) & zone(430, 705, 700, 1330))) & zone(280, 705, 200, 1850)
claim("mountain_rock", rock)

# No wizard_bear mask: the crag, wizard, and wall trees share the same green
# clusters, so color cannot split them. The wizard ships as the existing
# src/assets/wizard-bear.svg overlay in stage 2; the crag mass belongs to
# foreground_forest.

# River, claimed before mid_ridges: the upper winding course is partly cluster 1,
# which mid would steal. Rebuilt 2026-08-16 after Fedya flagged the outline: the
# old 9x9 open erased the thin upper switchbacks, and the sunlit valley-head
# meadow (color-identical to water, both cluster 5) stayed connected. Water and
# meadow cannot be split by color, so the meadow is cut by exclusion rects and
# the upper course is rescued by brightness (the winding line is brighter than
# the mist around it).
lab_L = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)[:, :, 0]
pale = in_clusters(5, 7, 13)
riverish = (pale & zone(830, H, 620, 1350)) \
    | ((pale | in_clusters(1)) & (lab_L >= 142) & zone(778, 830, 1000, 1180)) \
    | (in_clusters(1) & (lab_L > 128) & zone(830, 870, 1005, 1175))
meadow_cut = zone(868, 932, 848, 1040) | zone(932, 958, 848, 1012)
mist_cut = zone(795, 830, 990, 1058) | zone(795, 872, 880, 1008)
riverish &= ~(meadow_cut | mist_cut)
n, cc, stats, _ = cv2.connectedComponentsWithStats(riverish.astype(np.uint8), 8)
best, best_area = -1, 0
for i in range(1, n):
    reaches = stats[i, cv2.CC_STAT_TOP] + stats[i, cv2.CC_STAT_HEIGHT] > 1000
    if reaches and stats[i, cv2.CC_STAT_AREA] > best_area:
        best, best_area = i, stats[i, cv2.CC_STAT_AREA]
river = cc == best
# Reconnect pools and thin-course breaks near the main channel; the meadow
# cannot flood back in because it was removed from riverish outright.
near = cv2.dilate(river.astype(np.uint8), np.ones((17, 17), np.uint8)).astype(bool)
for i in range(1, n):
    if i != best and stats[i, cv2.CC_STAT_AREA] <= 1200 and ((cc == i) & near).any():
        river |= cc == i
claim("river", river)

# Mid ridges: the dark violet forest band in front of the mountain base.
mid = in_clusters(1, 8) & zone(600, 840, 300, 1750)
claim("mid_ridges", mid)

# Terraces: stepped fields right of the river.
terr = in_clusters(3, 4, 5, 11) & zone(820, 1080, 1120, 1680)
claim("terraces", terr)

# Green hills: sunlit valley slopes.
hills = in_clusters(3, 4, 5, 11) & zone(700, 960, 460, 1720)
claim("green_hills", hills)

# Foreground forest: dark walls left and right plus the bottom shrub band.
fg = in_clusters(2, 3, 4, 10, 11, 5) & (zone(380, H, 0, 620) | zone(380, H, 1560, W) | zone(920, H, 0, W))
claim("foreground_forest", fg)

# Sky: the remaining gradient. Gated above y=760 so pale river highlights that
# share cluster 7 fall to their true neighbors instead.
sky = in_clusters(0, 7, 9, 12) & zone(0, 760, 0, W)
claim("sky", sky)

# ---- absorb leftovers: each unset pixel takes its nearest assigned pixel's label
un = sem == UNSET
print("unassigned before absorb:", int(un.sum()))
if un.any():
    _, near = cv2.distanceTransformWithLabels(
        un.astype(np.uint8), cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    lut = np.zeros(near.max() + 1, np.uint8)
    lut[near[~un]] = sem[~un]
    sem[un] = lut[near[un]]

# ---- outputs ------------------------------------------------------------------
masks_dir = HERE / "masks"
masks_dir.mkdir(exist_ok=True)
info = {}
for i, name in enumerate(REGIONS):
    m = sem == i
    cv2.imwrite(str(masks_dir / f"{name}.png"), (m * 255).astype(np.uint8))
    mean = bgr[m].mean(axis=0)[::-1] if m.any() else [0, 0, 0]
    info[name] = {"area_pct": round(float(m.mean() * 100), 2),
                  "mean_rgb": [int(v) for v in mean]}
json.dump(info, open(HERE / "regions.json", "w"), indent=1)

palette = np.array([
    [255, 200, 60], [255, 140, 40], [40, 40, 200], [200, 200, 255], [120, 120, 160],
    [90, 60, 130], [180, 120, 200], [60, 90, 200], [120, 220, 255], [60, 170, 90],
    [30, 100, 40], [140, 80, 30], [20, 50, 25], [255, 190, 210],
], np.uint8)
overlay = (0.45 * bgr + 0.55 * palette[np.clip(sem, 0, len(REGIONS) - 1)][..., ::-1]).astype(np.uint8)
cv2.imwrite(str(HERE / "overlay.png"), overlay)

cols, pw, ph, cap_h = 4, W // 3, H // 3, 26
rows = (len(REGIONS) + 1 + cols - 1) // cols
sheet = np.zeros((rows * (ph + cap_h), cols * pw, 3), np.uint8)
panels = [("OVERLAY", cv2.resize(overlay, (pw, ph)))]
for i, name in enumerate(REGIONS):
    p = cv2.resize(((sem == i) * 255).astype(np.uint8), (pw, ph), interpolation=cv2.INTER_AREA)
    panels.append((f"{name}  {info[name]['area_pct']}%", cv2.cvtColor(p, cv2.COLOR_GRAY2BGR)))
for j, (title, panel) in enumerate(panels):
    r, c = divmod(j, cols)
    y = r * (ph + cap_h)
    sheet[y + cap_h : y + cap_h + ph, c * pw : (c + 1) * pw] = panel
    cv2.putText(sheet, title, (c * pw + 6, y + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
cv2.imwrite(str(HERE / "contact_sheet.png"), sheet)
for name, d in info.items():
    print(f"{name:<18} {d['area_pct']:5.2f}%  rgb {d['mean_rgb']}")
