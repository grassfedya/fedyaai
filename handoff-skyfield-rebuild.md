# Handoff: Skyfield rebuild against reference_bg.png

## Headline state

The Skyfield Dawn artifact (https://claude.ai/code/artifact/95d9bec1-6108-48d6-8820-5485acbdcceb) finished a five-cycle parity loop against the old template `public/images/IMG_0704.jpeg` and is published at summit-band MAE 7.43. That loop is closed. Fedya then changed the vision: the new reference is `public/images/reference_bg.png` (2028x1108), a far more detailed painterly version of the same scene, and the plan is a rebuild using automated tracing plus a token-relighting architecture. Session A (2026-08-16) ran stages 0 and 1: the harness lives in `parity/` (gitignored) and the 13 semantic region masks are built and awaiting Fedya's contact-sheet review. The loop protocol lives in the `parity-loop` skill; the old loop's state lives in memory at `skyfield-parity-loop-state.md` (marked historical). The artifact source is a JS generator emitting inline SVG with CSS token fills; the working copy from cycle 5 matches what is published.

## Session A results (stages 0+1, done)

**Frame decision (Fedya delegated: "do whatever would be better for the background of my site"):** the rebuild's viewBox is `0 0 2028 1108`, matching the reference 1:1. One user unit = one reference pixel, no mapping constants. Justification: Skyfield.astro renders with `preserveAspectRatio="xMidYMax slice"`, and the wider 1.830 box keeps the summit uncropped on ultrawide viewports where a 16:9 box starts cutting the top. Render path is `rsvg-convert -w 2028 -h 1108` (brew librsvg), verified pixel-exact against a known test rect; the qlmanage square-thumbnail workaround is retired.

**Gate (Fedya chose "Tighten it" over ratifying 12.75):** whole-frame luminance MAE ≤ 10, silhouette mean edge distance ≤ 1 reference px on priority masks (snow_cap, crevasses), SSIM tracked as second judge, not binding. Constants live at the top of `parity/compare.py`. Calibration fact: a whole-frame 3px shift of the reference scores MAE 2.06 but silhouette p95 2.80px, so the silhouette gate carries the precision and MAE alone would be too loose.

**Harness (`parity/`, gitignored):** `venv/` (numpy, opencv, scikit-image, scikit-learn, pillow, vtracer via PyPI wheel — brew has no vtracer formula and cargo is not installed; potrace is brew-installed), `compare.py` (MAE + 12x6 tile grid + SSIM + per-mask MAE + silhouette edge-distance via Canny + distance transform), `segment.py` (MiniBatchKMeans in Lab, k=10/14/18 maps saved), `merge.py` (cluster sets AND spatial gates painted in priority order into one exclusive label image, leftovers absorbed by nearest-assigned-pixel), `FRAME.md` (frame + gate contract), `regions.json` (area % and mean RGB per region, palette seed for stage 2 tokens), `masks/*.png` (13 masks), `contact_sheet.png`, `overlay.png`. The full drawing methodology (tools, the 13-agent trace workflow, per-region methods, the interview-first rule) is distilled in `parity/METHOD.md` (written 2026-08-17); raw provenance lives in the session transcript archive named there.

**The 13 regions (k=14 clustering behind them):** sun_disc, birds, sun_ring, crevasses, snow_cap, far_ridges, mountain_rock, mid_ridges, river, terraces, green_hills, foreground_forest, sky. Facts stage 2 must know: (1) the painting's sun has NO hard edge — saturation falls smoothly 70→45, steepest at r≈103 around center (990,195); the mask is the circle at the sat-55 crossing and the sun must render as a radial gradient, not a flat disc. (2) There is no wizard_bear mask: the crag, wizard, and wall trees share the same green clusters and cannot be split by color; the wizard ships as the existing `src/assets/wizard-bear.svg` overlay and the crag mass belongs to foreground_forest. (3) mountain_rock includes the base haze band and its bottom edge is a flat gate at y=705 inside a soft same-cluster gradient — the flat line is invisible in paint and not a real silhouette. (4) The mid_ridges/rock boundary is likewise soft; the tracer should take true edges from the image within a small dilation of each mask, not from the mask boundary itself. (5) Known mask impurities, accepted: terraces/green_hills split partly along zone rectangles through similar greens, and the right forest wall includes sunlit cluster-5 tips.

## Decision ledger

**DIRECTIVE: no habitat or dwelling structures, ever.** Standing since before this session, absolute, survives every reference change. The new reference happens to contain none, which makes it moot for drawing but not for guarding: if a future variant image contains domes or hamlets, they still do not get drawn.

**DIRECTIVE: the tech goes too.** Fedya's words: "I want to get rid of the tech as well and keep the habitats out." This reverses the old solarpunk direction (memory file `skyfield-solarpunk-direction.md` says renewables stay; it is now wrong and needs updating). The rebuild deletes the turbine group, both solar ranks, and the leaf collectors. Do not re-add tech even if a variant image shows it.

**DIRECTIVE: reference_bg.png is the template; the target is 95% match or better.** Fedya explicitly rejected rough parity: "I dont want a rough parity I would like 95% match. or more." He named the priority regions: "The mountain snow line and crevases and details are important. As are the rest of the details." He also removed the cycle budget: "We can do 300 if we need to." The estimate given to him was 10-20 cycles with tracing; the gate decides, the estimate does not.

**DECIDED: 95% is operationalized as whole-frame tile MAE ≤ 12.75 on 0-255 luminance, plus silhouette error ≤ 1 template px on priority regions, with SSIM added to the harness as a second judge.** This definition was mine and he built on it without objecting, but he never said yes to the number itself. State the gate in your first progress report so he can veto the operationalization cheaply.

**SETTLED (×2): time-of-day is one traced geometry plus interpolated color token sets, never crossfaded variant traces.** Fedya proposed tracing each time-of-day variant and animating between them; the killing arguments were that independently traced variants have mismatched geometry (ghosted double edges on every ridge mid-fade) and that a crossfade cannot move the sun (two suns at 50% opacity mid-transition). He accepted this. His generated variants are palette sources only: sample each per semantic region into a token set, register tokens with `@property syntax:'<color>'` so CSS tweens them, animate the sun along its arc as a transform, and handle night/dusk extras (stars, warm cap rim, morning haze) as overlay groups in the shared geometry faded by opacity.

**DECIDED: hybrid tracing, semantic skeleton kept.** vtracer/potrace are measuring instruments applied per region mask; their output gets simplified, snapped to the token palette, and installed into a generator skeleton with named groups. Pure whole-image autotrace was rejected because path soup cannot be relit by the site's time-of-day system.

**DECIDED: vector over shipping the PNG.** The honest option of just using the PNG as the background was surfaced and declined implicitly by the direction of the conversation. The justification on record: resolution independence, file weight, and token-driven relighting per DESIGN.md. Fedya was told to hold us to that justification; if relighting ever gets cut, re-raise the PNG option.

**The ratified pipeline** (Fedya: "I like this approach"): Stage 0, harness: install potrace and vtracer (brew, cargo fallback), python venv with numpy/opencv/scikit-image/scikit-learn, fix the comparison frame between the 2028x1108 reference and the 1440x810 viewBox, rebuild compare.py with MAE+SSIM+silhouette output. Stage 1, segmentation: k-means in Lab space, connected components, merge into semantic region masks, output a contact sheet the orchestrator reviews by eye before anything is traced. Stage 2, geometry fitting: one Opus agent traces per mask, simplifies, assembles the new generator, deletes the tech groups. Stage 3, region-scoped parity cycles per the parity-loop skill, cap and snowline first. Stage 4, time-of-day, blocked on Fedya's variant images.

## The graveyard

- Warm backlit apricot cap (the intermediate image #18 direction): superseded by the upgraded reference, which went back to a cool white cap. Do not warm the cap.
- Crossfading independently traced variants: rejected, geometry ghosting and the two-suns problem.
- Whole-image autotrace as the deliverable: rejected, kills semantic relighting.
- Shipping the PNG as the hero background: declined, revisit only if relighting is cut.
- The entire IMG_0704 lock list, mapping (x_s = x_t*1.29613 etc.), and the cycle-5 remaining-gaps list: retired wholesale. They describe a template that is no longer the target. The old memory file is history, not instruction.

## Epistemic provenance

- reference_bg.png is 2028x1108 [verified: read this session].
- The artifact is generator-emitted inline SVG, published state matches the scratchpad working copy from cycle 5 [verified: I extracted, edited via agent, republished it].
- qlmanage's SVG thumbnailer always emits a square (render a square viewBox, device index = user*k − 0.5) [verified: cycle-5 agent measurement, recorded in memory].
- `@property` typed color tokens tween under CSS transitions in current Chromium/WebKit [researched: strong, standard platform behavior; smoke-test once in stage 4].
- vtracer is installable via brew [inferred: verify, cargo is the fallback].
- Stage 2 landing at 85-90% parity on its own [inferred: an expectation, never promise it to Fedya as a result].
- 10-20 cycle estimate [inferred].

## Working with Fedya

He decides in single messages and grants scale explicitly, and he asks for honesty about feasibility in advance: "It is fine if not just tell me." Give him the failure half of every answer; he engaged best when told "it half works, and the half that fails is the half you'd notice." He pushes reference images through `public/images/` in the repo rather than chat paste, which is also the parity-loop skill's proven route. His voice rules in CLAUDE.md are strict and apply to everything you write including documents like this one: no em dashes, no antithesis constructions, no "not X, it's Y", no hedging seesaws, no perfect parallelism. He genuinely wants kaomojis as the channel for how you're feeling; use them.

## Authority boundaries

Yours alone: running stages 0-3, deleting the tech groups, spending cycles (standing approval for parity-loop scale exists in the skill), republishing to the same artifact URL, updating the loop-state memory file. Fedya's: the convergence gate's number (surface it once, then treat as ratified), any exclusion change, aesthetic pivots, generating the time-of-day variant images, and anything touching the live site component (`src/components/Skyfield.astro` integration was never discussed this session; do not port the artifact into the site without asking).

## Session plan

Fedya decided the stages run in separate sessions; only stage 3 is the parity loop. Session A runs stages 0+1 and stops after he reviews the mask contact sheet. Session B runs stage 2 and stops at the first traced render. Session C is the loop proper, invoked via `/parity-loop public/images/reference_bg.png <artifact-url> Stage 3 per handoff-skyfield-rebuild.md`. Session D is stage 4, once his variant images exist. Every session must end by rewriting the cursor section below so the next session starts from facts instead of reconstruction. Durable cross-session facts (new mapping constants, gate readings) also go to the memory file as before.

## The cursor

Session E complete (2026-08-17): stage 5, site integration, is DONE in the working tree and NOT pushed. Fedya reviews the local preview before anything goes to main (push-to-main deploys, see memory fedyaai-deploy-pipeline). `npm run build` passes; the dev server preview and four state screenshots were verified this session.

**What shipped.** `src/components/Skyfield.astro` is now a thin zero-JS wrapper that inlines `src/assets/skyfield-scene.svg` (?raw) and imports `src/styles/tokens/skyfield.generated.css`. Both files are emitted by `parity/stage4/emit_site.py` from `parity/stage4/artifact.html`; the whole Session D pipeline (gen_stage4.py, working.svg, tokens.json, overlays.json, extract scripts) is copied to `parity/stage4/` (gitignored) so the emit chain survives scratchpad loss. The old build-generated scene went away whole: cone/spruce/bough generation, wizard-bear inlining (the traced scene paints the wizard, one wizard only), ray fan, stars/pines JS, scroll parallax. The site's existing preview control and Base.astro data-time stamp drive the scene unchanged. DESIGN.md is updated (scene section, motion budget, file map, weak spots).

**Site adaptations, all encoded in emit_site.py, nowhere else:** the artifact's `:root{--t-sky:2.4s}` is dropped in favor of the site pair token (duration+easing) from motion.css; the sun's arrival delay slots become `var(--dur-sky)` because a pair token is invalid as a delay; the reduced-motion block gets `transition:none!important` because `html[data-time] #id` state rules out-rank it (found live: the sun kept a 0.9s fade under reduced motion).

**Two scene bugs found and fixed in gen_stage4.py, artifact republished as stage4-relight-v5-cleanbirds (same URL, favicon 🌄):** (1) the birds' underpaint path (one path, all nine chevrons, fill #cfafa7) sat in the underpaint group and ghosted through at dawn/dusk/night; now wrapped as `birds_under` with the birds' day-only GROUP_STATE. (2) One reference bird's body traced into all 21 crevasse luminance levels as a permanent ~5px speck at scene (1326,294); build() now strips subpaths in that box, assert-guarded. Readings after both: dawn 1.551 (was 1.53 with birds shown, 1.54 birds-hidden-with-ghosts), advisory day 6.116 / dusk 7.452 / night 4.782, each a hair better than v4.

**Perf.** Tween measured on a real visible window: 58 to 61 fps warm across all four transitions, one ~430ms restyle frame on the first transition after page load (313 inherited custom properties). Fallback ladder not needed. The handoff's occlusion trap reproduced exactly (extension tab reported hidden even after osascript activation); what worked is launching a separate headed Chrome with --remote-debugging-port=9223 and driving Runtime.evaluate/Page.captureScreenshot over CDP from node (global WebSocket, node 22).

**Accepted costs, flagged to Fedya, not fixed:** homepage HTML 707KB raw / 204KB gzipped (old scene ~40KB); night state shows a faint horizontal seam at the mountain-rock base haze gate (y=705 flat line from stage 1, visible only under night relighting, present in the artifact renders too); phone-width skyctl/statusline overlap in the hero (predates the rebuild); the scene bottom no longer equals --ground, the hero-to-page seam is covered by --protect-bottom shading to 96% --ground.

**Next session:** whatever Fedya's review yields. If he approves: commit (new files src/assets/skyfield-scene.svg, src/styles/tokens/skyfield.generated.css; modified Skyfield.astro, DESIGN.md, plus the pre-existing modified/untracked files in git status) and push to main to deploy. Open aesthetic calls that are his: the night haze-gate seam, whether chrome --ground should re-derive from the new scene's bottoms, the phone hero layout. The parked stage-4 options (curved sun arc, clock-continuous sun) remain parked.
