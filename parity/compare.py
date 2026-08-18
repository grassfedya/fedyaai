#!/usr/bin/env python3
"""Parity harness for the Skyfield rebuild against reference_bg.png.

Frame contract (see FRAME.md): both images must be exactly 2028x1108. The artifact
renders via `rsvg-convert -w 2028 -h 1108`, so device px == user px == reference px.

Gate: whole-frame luminance MAE <= 10, silhouette mean edge distance <= 1 px on
priority masks. SSIM is reported, not binding.

Usage:
  compare.py RENDER.png [--ref path] [--masks DIR] [--priority name1,name2] [--json OUT]

--masks DIR holds binary region masks (white = region) named <region>.png at
reference resolution. Per-mask MAE/SSIM is reported for every mask; silhouette
edge distance is computed for masks named in --priority (default: snow_cap,crevasses
when present).
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from skimage.metrics import structural_similarity

REF_DEFAULT = Path(__file__).resolve().parent.parent / "public/images/reference_bg.png"
W, H = 2028, 1108
TILES_X, TILES_Y = 12, 6
GATE_MAE = 10.0
GATE_SILHOUETTE_PX = 1.0


def load_gray(path):
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        sys.exit(f"cannot read {path}")
    if img.shape[1] != W or img.shape[0] != H:
        sys.exit(f"{path} is {img.shape[1]}x{img.shape[0]}, frame contract requires {W}x{H} (see FRAME.md)")
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float64)


def tile_mae(diff):
    rows = []
    for ys in np.array_split(np.arange(H), TILES_Y):
        row = []
        for xs in np.array_split(np.arange(W), TILES_X):
            row.append(float(diff[np.ix_(ys, xs)].mean()))
        rows.append(row)
    return rows


def edges(gray, mask=None):
    e = cv2.Canny(gray.astype(np.uint8), 40, 120)
    if mask is not None:
        zone = cv2.dilate(mask, np.ones((7, 7), np.uint8))
        e = cv2.bitwise_and(e, e, mask=zone)
    return e


def silhouette_distance(ref_gray, ren_gray, mask):
    """Mean/p95 distance from each reference edge px (inside the dilated mask zone)
    to the nearest render edge px. Measures how far the drawn boundary sits from
    the painted one without needing to segment the render."""
    ref_e = edges(ref_gray, mask)
    ren_e = edges(ren_gray, mask)
    if ref_e.sum() == 0:
        return None
    if ren_e.sum() == 0:
        return {"mean": float("inf"), "p95": float("inf"), "ref_edge_px": int((ref_e > 0).sum())}
    dist_to_render = cv2.distanceTransform(255 - ren_e, cv2.DIST_L2, 5)
    d = dist_to_render[ref_e > 0]
    return {"mean": float(d.mean()), "p95": float(np.percentile(d, 95)), "ref_edge_px": int(d.size)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("render")
    ap.add_argument("--ref", default=str(REF_DEFAULT))
    ap.add_argument("--masks", default=None)
    ap.add_argument("--priority", default=None)
    ap.add_argument("--json", dest="json_out", default=None)
    args = ap.parse_args()

    ref = load_gray(args.ref)
    ren = load_gray(args.render)
    diff = np.abs(ref - ren)

    out = {
        "mae": float(diff.mean()),
        "ssim": float(structural_similarity(ref, ren, data_range=255.0)),
        "tile_mae": tile_mae(diff),
        "regions": {},
        "silhouette": {},
    }

    mask_dir = Path(args.masks) if args.masks else None
    if mask_dir and mask_dir.is_dir():
        names = sorted(p.stem for p in mask_dir.glob("*.png"))
        if args.priority:
            priority = [n.strip() for n in args.priority.split(",")]
        else:
            priority = [n for n in ("snow_cap", "crevasses") if n in names]
        for name in names:
            mask = cv2.imread(str(mask_dir / f"{name}.png"), cv2.IMREAD_GRAYSCALE)
            if mask is None or mask.shape != (H, W):
                continue
            mask = (mask > 127).astype(np.uint8)
            sel = mask > 0
            if not sel.any():
                continue
            out["regions"][name] = {
                "mae": float(diff[sel].mean()),
                "area_px": int(sel.sum()),
            }
            if name in priority:
                out["silhouette"][name] = silhouette_distance(ref, ren, mask)

    sil_vals = [s["mean"] for s in out["silhouette"].values() if s]
    out["gate"] = {
        "mae_pass": out["mae"] <= GATE_MAE,
        "silhouette_pass": bool(sil_vals) and all(v <= GATE_SILHOUETTE_PX for v in sil_vals),
        "gate_mae": GATE_MAE,
        "gate_silhouette_px": GATE_SILHOUETTE_PX,
    }

    print(f"MAE  {out['mae']:.2f}  (gate <= {GATE_MAE}: {'PASS' if out['gate']['mae_pass'] else 'fail'})")
    print(f"SSIM {out['ssim']:.4f}  (tracked, not binding)")
    flat = [(v, x, y) for y, row in enumerate(out["tile_mae"]) for x, v in enumerate(row)]
    worst = sorted(flat, reverse=True)[:5]
    print("worst tiles (mae, col, row):", ", ".join(f"{v:.1f}@({x},{y})" for v, x, y in worst))
    for name, r in out["regions"].items():
        line = f"region {name:<18} mae {r['mae']:6.2f}"
        if name in out["silhouette"] and out["silhouette"][name]:
            s = out["silhouette"][name]
            line += f"  silhouette mean {s['mean']:.2f}px p95 {s['p95']:.2f}px"
        print(line)

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(out, indent=1))
        print(f"wrote {args.json_out}")


if __name__ == "__main__":
    main()
