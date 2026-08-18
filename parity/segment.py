#!/usr/bin/env python3
"""Stage 1 step 1: k-means clustering of reference_bg.png in Lab space.

Outputs per k:
  clusters_k{K}.png       cluster map recolored with each cluster's mean color
  clusters_k{K}_index.npy label image (H x W int)
  clusters_k{K}_sheet.png contact sheet: one panel per cluster, mask in white
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from sklearn.cluster import MiniBatchKMeans

HERE = Path(__file__).resolve().parent
REF = HERE.parent / "public/images/reference_bg.png"
W, H = 2028, 1108


def run(k):
    bgr = cv2.imread(str(REF))
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32)
    km = MiniBatchKMeans(n_clusters=k, random_state=7, n_init=10).fit(lab)
    labels = km.labels_.reshape(H, W)

    mean_bgr = np.zeros((k, 3), np.uint8)
    for i in range(k):
        mean_bgr[i] = bgr.reshape(-1, 3)[km.labels_ == i].mean(axis=0)
    cv2.imwrite(str(HERE / f"clusters_k{k}.png"), mean_bgr[labels])
    np.save(HERE / f"clusters_k{k}_index.npy", labels)

    cols = 4
    rows = (k + cols - 1) // cols
    ph, pw = H // 3, W // 3
    sheet = np.zeros((rows * (ph + 24), cols * pw, 3), np.uint8)
    for i in range(k):
        r, c = divmod(i, cols)
        panel = cv2.resize(((labels == i) * 255).astype(np.uint8), (pw, ph), interpolation=cv2.INTER_AREA)
        y = r * (ph + 24)
        sheet[y + 24 : y + 24 + ph, c * pw : (c + 1) * pw] = panel[..., None]
        share = (labels == i).mean() * 100
        cv2.putText(sheet, f"cluster {i}  {share:.1f}%", (c * pw + 6, y + 17),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, tuple(int(v) for v in mean_bgr[i]), 1, cv2.LINE_AA)
        cv2.rectangle(sheet, (c * pw + 170, y + 4), (c * pw + 200, y + 20), tuple(int(v) for v in mean_bgr[i]), -1)
    cv2.imwrite(str(HERE / f"clusters_k{k}_sheet.png"), sheet)
    print(f"k={k} done, shares:", " ".join(f"{i}:{(labels == i).mean()*100:.1f}%" for i in range(k)))


if __name__ == "__main__":
    for k in [int(a) for a in sys.argv[1:]] or [10, 14, 18]:
        run(k)
