# fedya.ai design system — "first light"

The direction in one line: an observatory in a forest. Solarpunk hope plus the Pythagorean
mystery-school register, executed as flat layered landscape, hairline gold geometry, and a
sky that follows the visitor's actual clock. This replaced the cyberpunk carbon/acid system
in August 2026. The full moodboard is at the bottom of this file.

## The one idea

The sky is set by the visitor's clock. `Base.astro` stamps `data-time` on `<html>` before
first paint; every color in the site derives from that state. Dark mode is not a toggle, it
is dusk arriving on schedule.

Buckets: dawn 05:00–08:00, day 08:00–17:00, dusk 17:00–21:00 (SSR default and the brand
state), night otherwise. The homepage has preview buttons bottom-right so nobody has to
wait for the planet; "now" returns to auto.

Everything that shows this off is real data. The weekday in the hero dateline is the actual
weekday, the clock is live. If a future element performs liveness without an underlying
fact, cut it.

## Color

Raw palette lives in `src/styles/tokens/palette.css`. Components never touch it; they use
`src/styles/tokens/semantic.css` only. That indirection is the reason the whole redesign
shipped without editing a single component, keep it sacred. The Skyfield scene is the one
exception, spelled out below.

### The Skyfield scene (August 2026 rebuild)

The hero landscape is a traced painting, not hand-drawn geometry. The scene is a
2028x1108 SVG traced from `public/images/reference_bg.png` (whole-frame luminance MAE
1.55 against it at dawn): the snow-capped summit with its crevasse detail, far and mid
ridge bands, the river winding through terraced fields, green hills, and a foreground
forest with the wizard painted into the right crag. Time-of-day relighting is 313
measured color tokens (`--t0` to `--t312`), registered with `@property syntax:'<color>'`
so CSS can tween them. Dawn values sit on `html`; `html[data-time="day|dusk|night"]`
override them with palettes sampled from `public/images/Day.png`, `Dusk.png`, and
`Night.png` by per-region luminance-quantile transfer. The sun physically travels to a
per-state seat as a composed CSS transform, and overlay groups fade per state: stars and
the moon at night, warm cap rim and horizon glow at dusk, the day halo, the flock of
birds at day only (a standing rule: the reference paints them at dawn, we do not).

The whole scene is generator output. `parity/stage4/gen_stage4.py` emits it from the
traced dawn geometry plus the three variant paintings, and `parity/stage4/emit_site.py`
adapts it for the site: `src/assets/skyfield-scene.svg` (the geometry, inlined by
`Skyfield.astro`) and `src/styles/tokens/skyfield.generated.css` (the tokens and state
rules). Edit neither by hand; change the generator and re-emit. This is the sanctioned
exception to the semantic-tokens rule: the Skyfield tokens ARE the component's palette,
measured from art, and nothing outside the Skyfield component may reference them.
`palette.css` and `semantic.css` keep governing the site chrome exactly as before, and
the scene's timing rides the same `--t-sky` / `--dur-sky` pair from `motion.css`.

The old build-generated scene tokens in `palette.css` (`--m1`, `--m2`, `--r1` to `--r6`,
`--sun-x/y`, `--stars`, `--ray-strength`, the haze mixes) are legacy: the chrome still
derives from `--ground` and the sky stops, but no component draws with the ridge and sun
tokens anymore. The scene's bottom edge no longer equals `--ground` either; the hero
lands on the page through `--protect-bottom` (texture.css), which runs the lower 62% of
the hero down to 96% `--ground`.

The dusk ramp, horizon to foreground, sampled off the moodboard:
`#F0A05E #C9825D #7C6357 #3F4F52 #2A3D43 #182B33 #0C1C24`.

One accent: gold (`--gold-400: #d9a45b` at rest). It is the sun's metal, used for links,
focus, the geometry lines, and the featured tile. There is no second accent. Signal hues
are muted and landscape-sourced: moss for success, mist for info, amber for warnings, ember
for danger. Text is warm paper (`#efe9db`) in every state; the page below the fold stays
deep in all four, only the hero sky goes light at noon.

## The geometry layer

This is the mystery-school register and the easiest thing to ruin. Ray fans, orbit rings
(one plain, one dashed), star-chart connecting lines, all held at exactly 1px so they read
as an astronomer's engraving. If a line gets thicker than a hairline, or the geometry gets
dense, it tips into woo. Sparse and thin, always.

The old texture set (CRT scanlines, hazard hatch, blueprint grid, vignette) was deleted on
purpose. Do not reintroduce grit; this world has atmosphere, not static.

## Type

- Display and HUD: Jost. Light (300) for headings, medium (500) for the small tracked-caps
  labels. The wide positive tracking (`--ls-hud: 0.22em`, hero dateline 0.38em) is the
  rainmeter register and carries the brand, so weight stays low even at small sizes.
- Body: Spectral. The variable is still called `--font-sans` for component compat; the body
  face is a serif and that is intentional.
- IBM Plex Mono survives for code blocks only. No mono in UI chrome.

Jost is loaded at 300/400/500 only; `--fw-semibold` and `--fw-bold` deliberately resolve
to 500.

### Long-form prose (blog posts)

`src/styles/prose.css`, imported by the post template only. The tracked-caps h1 in
`global.css` is for two-word page titles ("BLOG", "WORK"); article titles are sentence-case
Jost light at `--fs-h2` because real titles run long and wrap. The reading column is
`max-width: var(--measure)` centered on itself, not on `--container-narrow`, so the text
column is the thing that sits centered on the page. Rhythm comes from a flex column gap
(`--space-4`) with extra `margin-top` on h2–h4; markdown images get a hairline border and
`--radius-md`; blockquotes take a 1px `--border-accent` left rule. The date line and the
"← Writing" back link are the existing `.hud` micro-type, not new styles.

## Motion budget

Slow and scarce. The budget on any page:

- The sky crossfade (`--t-sky`, 2.4s) when the time state changes: all 313 scene tokens
  tween, the sun travels to its seat (holding full brightness until it lands behind the
  dusk ridge, then fading in 0.9s), and the moon rises 62px at night. This is the one
  deliberately glacial motion in the system. Measured at 58 to 61 fps in Chrome; the
  first transition after load pays one ~430ms restyle frame.
- The jack-of-all-trades letter scatter, which predates this system and earns its place.

The old scene's ray-fan draw-in and scroll parallax went with the rebuild; the traced
scene ships with zero JS.

Nothing below the fold animates on scroll. No staggered fade-ins, no hover scale, no
count-ups. `prefers-reduced-motion` zeroes all of it.

## Hard rules

- No eyebrows. The slot above the homepage headline holds the live dateline, which is data.
- Components reference semantic tokens only, never raw palette values, never literal hexes.
- Gaps for spacing between siblings, not stacked margins (4px base scale in `spacing.css`).
- New empty states use the star-dot or orbit textures in `texture.css`, not new ones.
- Stats and badges only when the underlying fact exists. The site currently has no
  testimonials, no stat rows, and no live badges because it has no such facts.

## File map

- `src/styles/tokens/palette.css` — raw colors, the four time states (chrome only now; the scene has its own generated tokens)
- `src/styles/tokens/semantic.css` — the only tokens components may use
- `src/styles/tokens/skyfield.generated.css` — the scene's 313 relighting tokens and state rules; generated, never hand-edited
- `src/styles/tokens/typography.css`, `fonts.css` — type scale and webfonts
- `src/styles/tokens/texture.css`, `elevation.css`, `motion.css`, `spacing.css`, `base.css`
- `src/styles/prose.css` — long-form article typography, imported by `src/pages/blog/[slug].astro`
- `src/components/Skyfield.astro` — thin wrapper that inlines the generated scene and imports its CSS
- `src/assets/skyfield-scene.svg` — the traced 2028x1108 scene geometry; generated, never hand-edited
- `parity/stage4/` (gitignored) — the generator pipeline: `gen_stage4.py` (scene + tokens from `working.svg` and the variant paintings), `emit_site.py` (adapts the artifact for the site). The published Claude artifact "Skyfield" is the canonical backup if this directory is lost
- `src/assets/wizard-bear.svg` — the wizard riding his bear. No longer inlined anywhere: the rebuilt scene paints the wizard inside the foreground forest. Kept with `wizard.svg` and `bear.svg` as source assets
- `src/layouts/Base.astro` — pre-paint `data-time` stamp, nav, footer
- Sky preview control and live dateline: `src/pages/index.astro`

## Moodboard

The images and references the system was built from, and what each one contributed.

- **The Forestry rainmeter wallpaper** (teal pine valley, geometric sun, "W E D N E S D A Y"
  tracked across the sky). The single biggest source: the entire dusk ramp is sampled from
  it, its sun already has the ray-line geometry, and the tracked weekday became the live
  hero dateline. The wider rainmeter genre also supplied the idea of a screen that tells
  time, which became the data-time system.
- **RIME** (white tower on sea cliffs). The hope pole. If the forest-dusk stuff ever gets
  heavy or gloomy, this is the corrective: white stone, sea light, one tower.
- **Ghibli, Laputa specifically**. Overgrown technology, gardens on ruins, the yearning-up
  register. More a mood than a technique; nothing is sampled from it directly.
- **Firewatch's site hero**. The canonical layered-parallax landscape on the web, the proof
  the Skyfield approach works as a website and not just a wallpaper.
- **Kurzgesagt**. Optimistic-tech flat illustration that never gets twee. The reference for
  how far to flatten the landscape shapes.
- **Alto's Odyssey**. Soft gradient restraint; how few colors a sky needs.
- **JPL "Visions of the Future" posters**. The ad astra + hope + retro yearning register,
  and free to use. Candidate art for future pages (404, misc).
- **Urania's Mirror star cards (1824) and Haeckel's Kunstformen der Natur**. Public domain
  sources for the mystery-school layer: celestial engravings and organic forms. The 1px
  engraving rule comes from how these plates look.
- **Stripe Press** — respected, rejected. Gets the reverence right but it is a bookshelf;
  this site has to be navigable daily. Too editorial.
- **Emergence Magazine** — rejected. Buries the reading experience under its own
  atmosphere. Standing warning: when a flourish costs usability, the flourish loses.

## Known weak spots

- At night the mountain base haze band's flat gate (y=705 in scene space, invisible in
  the dawn paint) reads as a faint horizontal seam across the rock. Inherited from the
  stage-4 relighting, present in the artifact too, not a port artifact.
- The scene SVG is 653KB raw, about 193KB gzipped, inlined into every page that renders
  the hero. Homepage only today; think before putting Skyfield on more pages.
- At phone widths the sky preview control and the statusline overlap in the hero. This
  predates the rebuild.
- The homepage serves 850KB of HTML before compression; the old scene was ~40KB. The
  trade was accepted for the painted scene, revisit if it ever bothers.
