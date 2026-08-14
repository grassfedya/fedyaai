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
shipped without editing a single component, keep it sacred.

Each time state defines a sky gradient (`--sky-top/mid/low/horizon`), a sun
(`--sun`, `--sun-glow`, `--ray`), the lone far peak (`--m1`, a Fuji cone with an
`--m1-snow` cap that re-tints per state: pink at dusk, gold at dawn, white at day, dim
moonlit blue at night), a shorter foothill range in front of its base (`--m2`), a
six-step ridge ramp (`--r1` horizon haze → `--r6` near treeline), and `--ground`. The
depth stack runs peak → foothills → six ridges → the overlook, and the overlook is
deliberately one-sided: a slope falls from the upper left with three irregular spruces
stepping down it (the biggest cropped by the top of the frame, so the visitor sits under
it), canopy boughs enter from the left edge as the closest plane, and the right ledge
stays low and open so the valley drains toward the peak — then a crag climbs back out
of it: one diagonal promontory (base x1146–1440) with stepped strata, a prow
overhanging the valley, and a stone fang at its outer edge, the mass in `--fg-deep`
with lit `--ground` faces along the sun side and the crest lips. The only figure in
the world, the wizard (`src/assets/wizard.svg`, inlined at build and flipped to face
the peak), stands on the crag's crest, pipe lit, boots at y≈640 — the height is tuned
to the band stack: his hat breaks the foothill line, his chest and robe land in front
of the r1/r2 haze bands, and his smoke clears those bright bands into the dark
foothills and sky; his figure remaps to the overlook plane and
his smoke strands stay in sun ink, so they re-tint with the sky: gold at dusk,
moon-white at night. Three hairline bird chevrons near the sun's dusk seat carry the
size of the valley. Value stretch, all derived tokens in `palette.css`: the overlook
planes sit below `--ground` (`--fg-deep` 24% toward black, `--canopy` 40%) so the
nearest things step forward, and the far ridges dissolve toward the horizon
(`--r1-haze` 42% into `--sky-horizon`, `--r2-haze` 16%) so distance reads as haze. The
mountains sit in front of the sun on purpose: dusk parks it on the crater rim, dawn
crests it over the eastern shoulder; at night the cone dissolves into the sky and only
the snow cap stays legible. The overlook lives at the edges of the 1440 viewBox, so
phone-width crops lose the canopy, spruces, and wizard; the peak stays centered and
survives every crop. Two structural tricks:

- `--ground` is both the darkest ridge and the page background, so the hero lands on the
  content with no seam.
- The cone and its snow cap are generated at build time in `Skyfield.astro` from the same
  two slope beziers, so the snow's edges always sit exactly on the silhouette. Change the
  slope constants in the frontmatter, not the path strings.
- Valley mist is two flat bands filled with a transparent `color-mix` of `--sky-horizon`
  (18% mid-valley, 26% on the near treeline), so the fog re-tints with the time of day
  for free. It pools at the valley edges and thins where the view opens to the peak; the
  near band paints over the pine feet so the treeline stands in it.
- Semantic surfaces and borders are `color-mix()`ed from `--ground`, so the entire chrome
  re-tints with the time of day. Nothing else needs to know the time exists.

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

## Motion budget

Slow and scarce. The budget on any page:

- The sky crossfade (`--t-sky`, 2.4s) when the time state changes, including the sun
  physically moving. This is the one deliberately glacial motion in the system.
- The ray fan drawing in on load (Skyfield only).
- A few pixels of ridge parallax on scroll.
- The jack-of-all-trades letter scatter, which predates this system and earns its place.

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

- `src/styles/tokens/palette.css` — raw colors, the four time states
- `src/styles/tokens/semantic.css` — the only tokens components may use
- `src/styles/tokens/typography.css`, `fonts.css` — type scale and webfonts
- `src/styles/tokens/texture.css`, `elevation.css`, `motion.css`, `spacing.css`, `base.css`
- `src/components/Skyfield.astro` — the landscape: the peak and its snow, foothills, ridges, sun, birds, stars, pines, the overlook spruces and canopy, parallax
- `src/assets/wizard.svg` — the wizard illustration, inlined into Skyfield at build; paints in `--r6`/`--sun` with fallbacks (the figure is remapped to `--fg-deep` on the way in)
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

- The day state is the least resolved: the sky mids read murky. Tune the five
  `[data-time="day"]` sky hexes in `palette.css` before calling it finished.
- The near treeline is still one repeated pine path, so up close it reads stamped. The
  overlook no longer shares it (the spruces and boughs are generated, seeded, in
  `Skyfield.astro`'s frontmatter), which contains the problem to the mid-distance band.
- The hero sun glow is two flat circles; a radial gradient would sit better at day.
