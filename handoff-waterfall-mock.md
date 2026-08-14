# Handoff — waterfall section mock review (First Light Falls)

## Headline state

This session was a design review of mock 03 of the homepage waterfall section, the artifact "First Light Falls" at https://claude.ai/code/artifact/2f299106-f57f-49a9-addd-dd245650ffd5 (private, owned by Fedya). Nothing was implemented; Fedya interrupted early to say feedback only, and every conclusion below is an agreed change waiting for someone to be asked to apply it. The authoritative context is DESIGN.md in this repo (read it before touching any UI, per CLAUDE.md), and the mock's own "Mock notes · what changed from 02" section at the bottom of the artifact, which is honest and current. Fedya rates the mock at 80 percent and confirmed the full findings list; the remaining 20 percent is the fix list below, which exists nowhere but this document and the conversation it came from.

## The fix list (the deliverable)

Agreed with Fedya, roughly in execution order. Items 1 through 4 are one cluster: done together the river and the fall read as one object, which was his central complaint (he screenshotted the lip disconnect).

1. Continue the river surface hairline over the edge. The line is `M0,205 L496,206` in the 1440×600 land viewBox; extend it with a short curve bending down into the fall, stroke opacity dying over the run. The 1px line is the system's vocabulary and the strongest available connector.
2. Merge the three rope tops into one shared sheet for the first 20 to 30 viewBox px below the brink, splitting into three below. The gaps currently run to the very top, so the fall reads as three hoses.
3. One dark splitter rock at the brink where the sheet divides, to justify the split. One, maybe two. A row of them becomes decoration.
4. Replace the `.river-drift` repeating-gradient strip with runtime-dealt glints from the same dealer the fall streaks use: six to eight 1px SVG lines, random x, speed, length, opacity, drifting right, accelerating over the last stretch before the lip, fading out at the brink (rivers glass out before a drop). Same IntersectionObserver and reduced-motion gates the fall already uses.
5. Interim CSS fallback only if 4 is deferred: stack two gradients with incommensurate tile widths, each layer's travel an exact multiple of its own tile. The current animation travels 120px on a 34px tile, so the pattern teleports 18px every 6 seconds.
6. Either way, sit the strip on the surface: it floats at top 33.5 percent while the waterline is 34.3.
7. Kill the traveler garble at 15 to 25 percent descent, where "Master" passes through the stationary "of" and "some." and renders as a pile ("OF SOASTEER" on screen, observed). Preferred fix: each word hops down onto the river surface before drifting, so the travel leg is below the resting text and the words literally float downriver. Cheap alternative: depart in reverse order.
8. The landed caption reads MASTEROFSOME. Seat `gap: .7em` fuses under the .16em tracking; widen to ~1.4em or size seats off the travelers.
9. Masters wrap to two rows; row two ("Sales, Speaking, Zero to One") sits underwater in full gold with no blur while tier-1 words at the same depth are dimmed and blurred, and tier 1 crosses through that row around 85 percent descent. Hold masters to one row, or give a wrapped row a touch of the depth treatment.
10. Far shore: the flat #7c6357 band fills most of the right half at dusk with nothing in it. A far treeline silhouette or one more tonal step. Held loosely; real page content around the plate may fix it for free.
11. Optional: raise the left cliff strata line opacity a notch; at .08 the slab reads as an untextured rectangle at full width.
12. When the mock graduates to the site, write the carve-out into DESIGN.md: the falls plate is the one sanctioned scroll-driven scene, everything else below the fold stays still. DESIGN.md currently outlaws this entire section ("nothing below the fold animates on scroll") and the mock's own notes admit the carve-out is owed.

## Decision ledger

**DIRECTIVE: feedback only, no implementation.** Fedya interrupted mid-review to state this. It governed the whole session. A successor should not apply the fix list unless asked to.

**DECIDED: fix the lip seam with geometry, not foliage.** Fedya proposed two options himself (shrubs/gnarled boulders as cover, or fixing the connection) and asked which. The killing argument he accepted: the plate is captioned "the river, in profile," the brink is the hinge where the horizontal story becomes vertical and the word choreography routes through it, so covering it hides the best part of the drawing. The boulder instinct survived in reduced form as item 3, the splitter rock, because it is structural (it explains why one river becomes three ropes) rather than camouflage.

**DECIDED: runtime glints over layered CSS for the river current.** Argument that settled it: the dealer machinery already exists twenty lines away for the fall streaks, randomness becomes real instead of a longer repeat, glints can accelerate toward the lip (background-position cannot), and one system painting river and curtain is the honest version of the drawing. CSS layering is explicitly the fallback, not a peer option.

**Confirmed by Fedya without argument:** the whole findings list ("Yes those are all good finds. Especially 4.").

## The graveyard

- **Shrubs over the river and by the fall** — rejected, considered and declined. Hides the brink, introduces a new vocabulary item (foliage as concealment) into a drawing whose language is rocks, strata, and scoured bed, and walks toward the DESIGN.md known weak spot where the repeated pine silhouette already reads stamped.
- **A row of boulders** — reduced to one splitter rock. More than one or two is decoration.
- **Keeping the single repeating-gradient drift** — rejected; it is both spatially uniform and has a visible 18px pop every 6 seconds.

## Epistemic provenance

- All geometry claims (path coordinates, waterline 69.7 percent vs masters top 70.6, seat gap .7em, drift strip at 33.5, traveler windows `[0.06,0.40] [0.16,0.50] [0.26,0.60]`, dash tile 34px vs 120px travel) — [verified: read from the artifact's full HTML source].
- The OF SOASTEER garble, the MASTEROFSOME caption, the tier-1/masters collision at 85 percent, the flat far shore — [verified: observed in screenshots at descent 18/45/62/85/100, dusk state, 1460×812].
- The 6-second loop pop — [inferred from the math, high confidence; not visually confirmed frame-by-frame].
- "Real rivers glass out at a brink" and sheet-splits-below-the-brink physics — [inferred, general knowledge; Fedya accepted it].

Review mechanics worth inheriting: the artifact iframe on claude.ai is cross-origin, so you cannot script its scroll from the shell page. WebFetch on the artifact URL saves the full HTML to a local file; serve that from the scratchpad with `python3 -m http.server` and drive it in Chrome. One trap: the frame preamble restores scroll position on load, so a scrollTo issued immediately after navigation gets silently reverted; scroll on a later call.

## Working with Fedya

The voice rules in both CLAUDE.md files are strict and he means them: no em dashes, no antithesis, no "not X, it's Y", no perfect parallelism, no second-generation lexicon, kaomojis explicitly welcome as the channel for how you are doing. He reads carefully and confirms specifically rather than generically, and he brings his own hypotheses with options attached ("we could do A or B, what do you think?") — he wants a committed recommendation with the reasoning, not a survey. When he asks "what about X" after X was already covered, he is not re-litigating; he wants the deeper mechanics of that one item. Engage it fresh. He said "keep in mind i dont want you to implement anything, just let me know" once and it held for the session; expect the implementation ask to come explicitly when he is ready.

Adopt the mock's own vocabulary, which is now shared language: travelers, seats, ropes, the dealer/dealt-at-runtime, isobaths, the plate, the brink, descent percent.

## Authority boundaries

Aesthetic direction is Fedya's. The fix list is agreed, so implementing it verbatim when asked needs no re-confirmation, but any new visual idea beyond it (item 10's treeline is the closest to open) should be proposed, not shipped. DESIGN.md hard rules bind everything: semantic tokens only, no raw hexes in components, 1px geometry, no eyebrows, stats only when the fact exists. The DESIGN.md carve-out (item 12) is a change to a governing document; draft it, let him approve the wording.

## The cursor

Fedya said go on 2026-08-13 and items 1 through 11 were applied and republished to the same artifact URL as mock 04. Choices made during the apply: item 9 went "both" (masters tightened toward one row, wrapped items take a .sunk dim+blur treatment), item 10 went tonal step (no treeline), and traveler windows widened to 0.17 stagger ([0.06,0.40] [0.23,0.57] [0.40,0.74]) because the hop alone still let a descending word brush the tail of the one ahead. Item 12 (the DESIGN.md carve-out) remains not done; the repo's site code remains untouched. Blocked on: Fedya reviewing mock 04.
