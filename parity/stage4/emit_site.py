"""Emit the site-integration files from the stage-4 artifact.

Reads artifact.html (the canonical output of gen_stage4.py, label
stage4-relight-v3-sunhold + day-only birds) and writes:

  src/styles/tokens/skyfield.generated.css   scene tokens + state CSS
  src/assets/skyfield-scene.svg              the traced 2028x1108 geometry

Site adaptations applied here, nowhere else:
  1. The artifact's `:root{--t-sky:2.4s;}` is dropped. The site's
     tokens/motion.css owns --t-sky as a duration+easing pair
     (var(--dur-sky) var(--ease-sky)); every `... var(--t-sky)` slot in
     transition lists accepts the pair form, and prefers-reduced-motion
     zeroing of --dur-sky comes with it.
  2. The sun's arrival delay `opacity 0.9s ease var(--t-sky)` needs a bare
     <time> in the delay slot, so it becomes `... var(--dur-sky)`.
  3. The artifact page chrome (html,body reset, .skyfield layout, .hud) is
     cut; Skyfield.astro owns the wrapper, the site owns the preview control.
"""

import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
REPO = HERE.parent.parent
html = (HERE / "artifact.html").read_text()

# ---- CSS ----
css = html.split("<style>", 1)[1].split("</style>", 1)[0]

assert css.lstrip().startswith(":root{--t-sky:2.4s;}"), "artifact CSS shape changed"
css = css.replace(":root{--t-sky:2.4s;}", "", 1)

delay_fixed = css.count("opacity 0.9s ease var(--t-sky)")
assert delay_fixed == 2, f"expected 2 delay-slot uses of --t-sky, found {delay_fixed}"
css = css.replace("opacity 0.9s ease var(--t-sky)", "opacity 0.9s ease var(--dur-sky)")

cut = css.find("html,body{")
assert cut != -1 and "prefers-reduced-motion" in css[:cut], "page-chrome tail not where expected"
css = css[:cut]

# The artifact's reduced-motion block loses to the per-state group rules on
# specificity (html[data-time] #id beats a bare #id in a media query), which
# would leave the sun's fixed 0.9s/1.2s opacity fades alive. !important ends
# that; --dur-sky:0 from motion.css already zeroes everything var-driven.
rm = re.search(r"@media \(prefers-reduced-motion: reduce\)\{[^}]*\{transition:none;\}\}", css)
assert rm, "reduced-motion block missing"
css = css.replace(rm.group(0), rm.group(0).replace("transition:none;", "transition:none!important;"))

# Every remaining --t-sky must sit in a duration+easing slot of a transition
# list, where the site's pair token is valid.
for m in re.finditer(r"[^,:{]*var\(--t-sky\)", css):
    frag = m.group(0).strip()
    assert re.fullmatch(r"(--t\d+|opacity|transform|background) var\(--t-sky\)", frag), frag

header = """/* GENERATED FILE — do not edit by hand. gen_stage4.py owns this.
   Regenerate: python parity/stage4/emit_site.py (reads parity/stage4/artifact.html,
   itself emitted by gen_stage4.py from working.svg + the time-of-day variant images).

   The Skyfield scene's palette: measured color tokens (--t0..) registered
   with @property so they tween, dawn values on html, overrides per
   html[data-time="day|dusk|night"], plus per-group state rules (sun travel, moon,
   stars, birds at day only, dusk rim/horizon). Timing tokens --t-sky / --dur-sky
   come from tokens/motion.css. This file is the ONE exception to the
   "components use semantic tokens only" rule: these tokens ARE the scene,
   sampled from the reference paintings, and nothing outside the Skyfield
   component may reference them. */
"""
(REPO / "src/styles/tokens/skyfield.generated.css").write_text(header + css.strip() + "\n")

# ---- SVG ----
m = re.search(r"<svg[^>]*>[\s\S]*</svg>", html)
assert m, "no svg found"
svg = m.group(0)
assert "<script" not in svg

svg_header = (
    "<!-- GENERATED FILE - do not edit by hand. gen_stage4.py owns this\n"
    "     (parity/stage4/, regenerate via emit_site.py). The stage-4 Skyfield scene:\n"
    "     2028x1108 traced geometry from reference_bg.png, colors via classes\n"
    "     resolved in tokens/skyfield.generated.css. -->\n"
)
(REPO / "src/assets/skyfield-scene.svg").write_text(svg_header + svg + "\n")

print(f"css {len(css)/1024:.1f}KB  svg {len(svg)/1024:.1f}KB")
