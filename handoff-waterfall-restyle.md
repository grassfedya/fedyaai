# Handoff — waterfall restyle: text scheme swap, Firewatch parity, site integration

## Headline state

The homepage waterfall section exists as two private artifacts, both owned by Fedya: "First Light Falls" (with solarpunk structures, parked untouched) at https://claude.ai/code/artifact/2f299106-f57f-49a9-addd-dd245650ffd5 and "Wild First Light" (nature cut, the base going forward) at https://claude.ai/code/artifact/a8b36873-9701-49fd-abb2-77dbf6a8e4ee. **Pass 1 is DONE** (2026-08-16, published as mock 06 at the same URL, favicon 🏞️): the travel choreography is deleted and the text scheme is in, revised once by Fedya the same day (see the plan below for what actually shipped, which differs from the original pass-1 spec). The successor's mandate is pass 2. The repo is untouched except handoff docs; DESIGN.md and the earlier handoff-waterfall-mock.md in the repo root are required reading, and CLAUDE.md's voice rules govern everything you write.

## The plan (agreed, in order)

**Pass 1 — text scheme, in the nature-cut artifact. DONE, as mock 06.** What shipped, after one revision round from Fedya:

- The travel choreography is deleted wholesale: wade/ride/fall legs, scrub windows, travelers, seats, splash rings, the frame push-in, the descent counter. NOT deleted, against this doc's original instruction: #rvCenter, RV_HW, shLeft/shRight and their sampling code — the dealer's glints ride the centerline and its streaks ride the sheet edges, so those helpers live as long as the dealer does.
- "Jack of all trades." stands ON LAND, not on the river (first cut had it on the river's straight reach, angled 5.6°; Fedya killed that placement the same day: "keep it nice and large and visible. Flat, not angled. On the ground near the river"). It sits on the plateau's left field at left 5.5% / top 30%, mega scale (clamp 21–38px), paper color, flat, always visible.
- "Master of some." sits flat on the plunge basin (left 60.1% / top 75.5%, ~20px, --sunk). The 24 skill words are hand-placed on open water around it: mastered crisp in --sunk, the rest in depth tones + sub-pixel blur.
- A reveal-only scrub on a 220vh sticky track (Fedya asked for the reveal back): line 1 always shown, "Master of some." fades up over p 0.08–0.28, the skills fade in y-sorted top-to-bottom across p 0.32–0.92 with a 5px settle. Opacity only, nothing travels. Scroll cue restored. Reduced motion and no-JS show everything at rest.
- The slow drift on sunk skills was built and cut: the scatter packs to 1–2px gaps, so any visible wander collides. Do not revive.
- Bug found in review, fixed: --depth-1 mixed toward --ground and out-darkened --sunk, inverting the mastered/sunk hierarchy on the bright water. It now mixes 82% water-deep toward water-lo, and every depth tone must stay lighter than --sunk. Depth words are weight 300.
- Open judgment call, flagged to Fedya: the reveal order interleaves mastered and sunk words (pure y-sort). Mastered-first-as-a-beat is a three-line change if he wants it.
- Known accepted limits: the deepest tier is very faint at night; below 720px the smallest words stop being readable.

**Pass 2 — de-Poptropica via /parity-loop against a Firewatch reference.** The diagnosis Fedya accepted: the cartoon read comes from interior detail on planes (crop rows, moss interiors, ripple arcs, strata fills), no atmospheric haze ramp, and a thirty-plus-token palette. The fix: flatten plane interiors so detail lives only in silhouette edges, re-derive every plane value as a depth-stepped color-mix toward --sky-horizon (the exact recipe Skyfield already uses, --r1-haze is 42% into the horizon [verified: DESIGN.md]), collapse the palette toward the site ramp, drop rim edge-lighting on near planes. Fold the species swap into this pass since it is all silhouette work: palms → irregular spruce stands, monstera frame → conifer boughs (the hero's own nearest-plane device), making the falls the site's valley floor. CRITICAL caveat to bake into every loop brief: the Firewatch image is a STYLE target (haze, flatness, palette count), never a composition target — a naive parity run will try to redraw the falls into Firewatch's ridgelines and lookout tower. Capture the reference yourself by screenshotting the firewatchgame.com hero in Chrome unless Fedya hands you a specific frame; my belief that the site hero is dusk-orange-over-ridges is [inferred — verify when you screenshot].

**Pass 3 — camera, only if needed, and only with Fedya's judgment.** After pass 2, he judges whether it still reads map-like. If yes: lower the camera, pull back, compress the plan-view plateau to a band, more sky, river as ribbon. The old blocker (words needed a wide river to ride) died with the choreography, but the order stands: subtraction and haze first, camera last, because camera moves force regenerating geometry.

**Pass 4 — port into the site.** FallsPlate.astro component; strip mock chrome (embedded base64 Jost, the clock, the skyctl, the notes section); NO frame — top edge dissolves into a canopy band held at --ground, bottom lands on --ground through the foreshore; sky and sun wired to the hero's actual tokens; water as new raw tokens in palette.css exposed through semantic.css (components touch semantic only, hard rule); one sitting of dusk eye-tuning against the hero; a DESIGN.md edit sanctioning the ambient motion (pass 1 shrinks this from a carve-out paragraph to a footnote) — draft it, Fedya approves the wording.

## Decision ledger

**DECIDED (2026-08-16, revision round): line 1 lives on land, large, flat.** Fedya's words: "lets not make the text in the river. Just keep it nice and large and visible. Flat, not angled. On the ground near the river." Both lines flat, zero rotation. Do not put headline text on the river again.

**DECIDED (2026-08-16, revision round): the scroll reveal exists, but it only reveals.** Line 1 always shown; scroll fades in "Master of some.", then more skills with more scrolling. Opacity on a 220vh track. This replaces "everything static" from the original pass-1 spec and does NOT reopen the travel choreography.

**DECIDED: choreography dies, static two-line scheme replaces it.** Fedya proposed it himself. Killing argument: the choreography was the single constraint blocking Firewatch distance/haze/camera, and DESIGN.md's own standing warning (a flourish that costs usability loses) applied — assembling "MASTER OF SOME" over 100% of a scroll track costs the reader. Do not propose reviving it or a "lite" version.

**DECIDED: flush integration, not plate framing.** He said "I dont like the plate, i would rather it looks flush with my site." Flush means same world, which is what forces the species swap and the shared sky tokens. The atlas/engraving-plate framing argument is dead even though it was elegant.

**DECIDED: nature cut is the base for everything forward.** The structures artifact stays parked at its own URL, untouched, as its own thing.

**DECIDED: subtraction/haze before camera.** Evidence cited and accepted: the distant second waterfall is the least cartoony element in the plate because distance stripped it to two values — value compression did it, not the camera.

**DECIDED: /parity-loop is the vehicle for pass 2, style-target caveat mandatory.** Pass 1 is a normal fix round, no loop.

**DIRECTIVE (standing, from the build): Opus subagents** ("Use opus subagents please"), and the loop shape is agent → your OWN screenshot review against the reference → fix agent → repeat. Agents self-review before returning, and you still verify independently; every round in the build phase, my review caught things the agent's self-review missed.

**Settled during the build, still binding:** all four time states must hold with dusk as the judged state; every SVG fill/stroke is var()/color-mix() of per-time-state tokens, zero literal hexes in markup; 1px strokes carry vector-effect="non-scaling-stroke".

## The graveyard

- **Line 1 on the river** — built (angled 5.6° on the straight reach, placed off #rvCenter geometry), killed by Fedya on sight: too small, and he wants it flat on land. Dead.
- **Slow drift on the sunk skills** — built and cut in the same round; the scatter's tightest pairs sit 1–2px apart, so any visible amplitude makes words touch.
- **Deleting #rvCenter/RV_HW** — this doc originally ordered it; wrong. The dealer rides those paths. They stay.
- **Plate/atlas framing** — rejected by Fedya explicitly. Dead.
- **Riding-the-river choreography** — rejected by Fedya, his own call against his own flagship feature. Its machinery still lives in both files and pass 1 must delete it, not gate it.
- **The tropical references as parity target** — superseded. base-color.png / base-silhouette.png were the build targets; they are no longer what the scene should match. Do not "fix" pass-2 output back toward them.
- **Distance alone as the de-cartooning fix** — his hypothesis, graded partially right; folded into pass 3 as last resort.
- **Gold text on the lake** — killed during phase 4 of the build, measured ~1.5:1 contrast. Landed text is dark. Do not reintroduce.
- **Lateral plane parallax** — dropped in the build; every plane is cut by the plate edges, sliding opens gaps. A 2.2% frame push-in replaced it.

## Epistemic provenance

The scene geometry claims in the old handoff and agent reports (lip at 706–787/y197, viewBox 1440×600, the x=524 headland seam) are [verified: measured from the artifact source]. The Skyfield haze recipe and all site rules are [verified: DESIGN.md]. The Poptropica diagnosis (interior detail + no haze + palette count) is [inferred, argued, and accepted by Fedya — treat as design direction, not fact]. The firewatchgame.com hero's current appearance is [inferred from memory — verify by loading it]. The parity-loop skill interface (/parity-loop <template-path> <artifact-url>) is [verified: skill listing].

## Mechanics worth inheriting

Recover the artifact source with WebFetch on the artifact URL (it saves full HTML to a local file; the artifact body starts after `<body>` in the publish wrapper, and strip the trailing `</body></html>` too — this session's working copies live in a session-scoped scratchpad that may not survive). Serve locally with `python3 -m http.server` and drive in Chrome. The page's clock re-stamps data-time, so pin a sky state by clicking the skyctl button, never by setting the attribute (calling the button's .click() from the JS tool counts as clicking and is more reliable than coordinate clicks, which miss). One tooling wall hit by two sessions now: the Chrome MCP tab reports visibilityState "hidden", which freezes rAF and IntersectionObserver, so the dealer's motion cannot be watched through it — verify the dealer by diffing its code against the recovered original instead. Republishing to the same URL requires publishing the same file path from the owning conversation or passing `url:` from a new one — without `url:` you will mint a new artifact. The night moon sits at --sunx:67% deliberately (was 87%, hid behind a cloud bank). Both artifacts shared byte-identical scene markup before the fork; pass 1 only moved the nature cut, so that coupling is over.

## Working with Fedya

The old handoff's section stands (read it). New observations from this stretch: he reflects between sessions and returns with a taste verdict plus his own remedy hypothesis with options attached ("is it adding distance?") — he wants a committed recommendation with reasoning, and he will accept "partially right, here's the constraint" as an answer. A trailing "right?" wants a real yes-or-no with the reasoning, not affirmation. He killed his own most distinctive feature the moment the constraint was laid out, so argue the design honestly rather than protecting things he built affection for. Shared vocabulary now includes: the nature cut, the structures version, pass 1 through 4, the sunk treatment, the dealer, the brink, the plate (the scene div — the word survives even though the framing died). Kaomojis in every substantive message; he asks for them.

## Authority boundaries

Aesthetic direction is Fedya's. You may execute passes 1 and 2 without re-asking (this handoff is the go), including republishing the nature-cut artifact at its existing URL as you iterate. Pass 3 requires his judgment call after seeing pass 2. Pass 4 touches the repo; his pattern all through this work has been explicit go-ahead before repo changes, so present pass-2 results and ask before porting. The DESIGN.md footnote and the choice of a specific Firewatch frame are his approvals. New visual ideas beyond the agreed plan get proposed, not shipped.

## The cursor (updated 2026-08-16 evening: pass 2 done)

Pass 2 shipped as mock 07 to the nature-cut URL: four Opus parity cycles (~800k subagent tokens) against the firewatchgame.com hero as a style-only template (its logo is parallax layer keyart-2; hide it via JS before screenshotting). What shipped: a 14-rung depth ladder (--dp1..--dp14, --sky-horizon mixed toward per-state warm anchor --haze-deep), flattened plane interiors, water as sky reflection through the sun tokens with the sunk-text ordering verified in all four states, palms/monstera swapped for seeded spruces and conifer boughs in Skyfield's silhouette language, clouds lighter than their local sky. Remaining gaps all trace to locks (night ladder compression, day's near-white horizon, water fills) or to composition (the empty band between rim and basin, the mesa profile) — which is exactly the pass 3 question. Blocked on: Fedya judging mock 07. The original cursor below is historical.

## The cursor

Closed: the aerial trace build (7 agent rounds), the river bend/source geometry fix, and pass 1 (2026-08-16: one Opus agent round for the edit, my independent screenshot review catching the depth-tone inversion, then Fedya's same-day revision to the land placement plus the reveal scrub, shipped as mock 06 to the nature-cut URL). Working copy at the session scratchpad's pass1/wild-first-light.html; recover from the artifact URL if gone. Nothing is mid-flight. Live next actions in order: (1) Fedya's verdict on mock 06 (including the open reveal-order call); (2) screenshot the firewatchgame.com hero as the style template; (3) run /parity-loop for pass 2 with the style-not-composition caveat; (4) show Fedya, get the pass-3 judgment; (5) on his go, pass 4 into the repo plus the DESIGN.md draft. Blocked on Fedya at steps 1, 4 and 5.
