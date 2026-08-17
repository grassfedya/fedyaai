# Skyfield tracing method

How reference_bg.png became src/assets/skyfield-scene.svg, written so the next rebuild reruns the process instead of excavating transcripts. Full provenance (the workflow script, all 13 tracer manifests, every agent transcript) survives at `~/.claude/projects/-Users-fedyamuzyka-projects-fedyaai/86642c34-*/` (workflows/ and subagents/), sessions 2026-08-16/17.

## Interview Fedya first

Before any pixel work, resolve ambiguity by asking. On this project the calls only he could make: what "match" means as a number (he rejected rough parity and named 95%+), which regions carry priority (the snow line and crevasses), standing exclusions (no habitats, no tech), the cycle budget (uncapped), the frame (delegated). State your operationalization of his answer (the gate: whole-frame MAE <= 10, silhouette <= 1px on priority masks) in the first progress report so a veto costs him one message. Record decisions and rejected directions in the handoff doc as they happen. An ambiguity discovered mid-trace costs a redraw cycle; a question costs a sentence.

## Tools

- `parity/venv`: numpy, opencv, scikit-image, scikit-learn, pillow, vtracer (PyPI wheel)
- potrace (brew), rsvg-convert (librsvg; pixel-exact at `-w -h`, never qlmanage)
- `compare.py`: whole-frame MAE, 12x6 tile MAE, SSIM, per-mask MAE, silhouette mean edge distance (Canny + distance transform)
- `segment.py` / `merge.py`: Lab-space k-means maps (k=10/14/18), then cluster sets plus spatial gates painted in priority order into 13 exclusive region masks

## Approach

1. **Segment.** k-means in Lab, merge into semantic masks, contact sheet, Fedya reviews by eye before anything is traced.
2. **Trace via workflow.** 13 parallel Opus agents, one per region. Each gets: the reference, its mask labeled APPROXIMATE (take true edges from the image within ~8px, never from the mask boundary), a brief carrying the measured facts for its region, z-order with overfill rules (overfill up to 8px where a nearer layer covers you, hold visible silhouettes to 1-2px), and a verification contract: render your fragment with rsvg-convert, iterate to IoU >= 0.90 and in-mask MAE <= 14, return a structured manifest with real numbers.
3. **Let each agent pick its method.** Painterly regions: posterize into tones, trace each tone through potrace or findContours + approxPolyDP, stack fills big-base-first. Parametric regions get fits instead of traces: least-squares gradient stops for sky and river, circle fit via alpha unmixing for the sun, grid-searched center for the ring ornament, hand Béziers for smoke. Forcing one technique on all 13 regions would have lost the four best fragments.
4. **Assemble.** Concatenate fragments in z-order, put a vtracer underpaint (half-res reference, polygon mode) at the bottom so no gap reaches background, measure with compare.py.
5. **Parity cycles** per the parity-loop skill. One Opus agent per cycle, 3-4 scoped goals from the tile and silhouette readings. Rebuild the worst regions with masks rederived from the reference, since the stage-1 masks betray at their boundaries. The cycle-4 pattern for color: cumulative luminance stack, then disjoint chroma patches on top (split each level by Lab (a,b), emit a patch only where its median color beats the level fill).
6. **Freeze geometry after the loop.** Time-of-day is tokenized fills tweened by CSS, one geometry forever.

## Rules that cost cycles to learn

- Masks only select which pixels to look at. Every edge that ships comes from the paint itself. Both visible artifacts of the project (snow halo, crevasse box seams) were mask boundaries leaking into the drawing.
- A simplified contour covers different pixels than its input mask; approxPolyDP bulges. Rasterize your own output back and measure that.
- Underpaint everything. One uncovered row of pixels measured MAE 138.

Result on record: cycle 0 at MAE 2.449 / SSIM 0.945; after four cycles MAE 1.533 / SSIM 0.969, silhouettes 0.45px and 0.60px against the 1px gate.
