#!/usr/bin/env python3
"""Stage 4 generator: tokenize working.svg into the @property relight
architecture. Emits artifact.html (CSS custom-property tokens, data-time
states, 2.4s tween, preview buttons) and baked_{state}.svg (plain hexes,
for rsvg-convert measurement).
"""
import cv2, json, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sample_variants import (load_rgb, lum, eroded_mask, build_transfer, hex2rgb,
                             rgb2hex, bright_blob, ROOT, SP, W, H, REGIONS)

STATES = ["dawn", "day", "dusk", "night"]
VKEY = {"day": "Day", "dusk": "Dusk", "night": "Night"}

SUN_T = {
    "dawn":  "translate(0 0) translate(1013 209) scale(1) translate(-1013 -209)",
    "day":   "translate(3.2 -59.5) translate(1013 209) scale(0.484) translate(-1013 -209)",
    "dusk":  "translate(804 280) translate(1013 209) scale(0.9) translate(-1013 -209)",
    "night": "translate(804 280) translate(1013 209) scale(0.9) translate(-1013 -209)",
}
MOON_T = {
    "dawn":  "translate(0 62)",
    "day":   "translate(0 62)",
    "dusk":  "translate(0 62)",
    "night": "translate(0 0)",
}
TRANSFORMS = {"sun_travel": SUN_T, "moon": MOON_T}
def css_t(t):
    return re.sub(r'translate\(([-\d.]+) ([-\d.]+)\)', r'translate(\1px, \2px)', t)

GROUP_STATE = {  # id -> {state: opacity}
    "sun_travel":    {"dawn": 1, "day": 1, "dusk": 0, "night": 0},
    "sun_ring":      {"dawn": 1, "day": 0, "dusk": 0, "night": 0},
    "birds":         {"dawn": 0, "day": 1, "dusk": 0, "night": 0},
    "birds_under":   {"dawn": 0, "day": 1, "dusk": 0, "night": 0},
    "day_halo":      {"dawn": 0, "day": 1, "dusk": 0, "night": 0},
    "sky_warm_rect": {"dawn": 1, "day": 0, "dusk": 0, "night": 0},
    "stars":         {"dawn": 0, "day": 0, "dusk": 0, "night": 1},
    "moon":          {"dawn": 0, "day": 0, "dusk": 0, "night": 1},
    "night_fx":      {"dawn": 0, "day": 0, "dusk": 0, "night": 1},
    "dusk_rim":      {"dawn": 0, "day": 0, "dusk": 1, "night": 0},
    "dusk_horizon":  {"dawn": 0, "day": 0, "dusk": 1, "night": 0},
    "dusk_front":    {"dawn": 0, "day": 0, "dusk": 1, "night": 0},
    "dusk_sky_lr":   {"dawn": 0, "day": 0, "dusk": 1, "night": 0},
}

MANUAL = {  # (scope, dawnhex) -> {state: hex} partial overrides
    ("sun_disc", "#f6c7a9"): {"day": "#fdf6dc"},
}

def doc_segments(svg):
    """Split into top-level chunks: ('defs'|group-name|'raw', text)."""
    out = []
    pos = 0
    header_end = svg.index('<defs>')
    out.append(("raw", svg[:header_end]))
    defs_end = svg.index('</defs>') + len('</defs>')
    out.append(("topdefs", svg[header_end:defs_end]))
    rest = svg[defs_end:]
    depth = 0; start = None; name = None; last = 0
    for m in re.finditer(r'<g\b[^>]*>|</g>', rest):
        t = m.group(0)
        if t.startswith('</'):
            depth -= 1
            if depth == 0:
                out.append((name, rest[start:m.end()]))
                last = m.end()
        else:
            if depth == 0:
                start = m.start()
                idm = re.search(r'id="([^"]+)"', t)
                name = idm.group(1) if idm else '(anon)'
                if last < start:
                    out.append(("raw", rest[last:start]))
            depth += 1
    out.append(("raw", rest[last:]))
    return out

class Tokens:
    def __init__(self):
        self.bykey = {}   # (scope, dawnhex) -> tid
        self.vals = {}    # tid -> {state: hex}
    def get(self, scope, dawnhex):
        k = (scope, dawnhex.lower())
        if k not in self.bykey:
            self.bykey[k] = f"t{len(self.bykey)}"
        return self.bykey[k]

def main():
    svg = open(f"{SP}/working.svg").read()
    ref = load_rgb(f"{ROOT}/public/images/reference_bg.png")
    variants = {s: load_rgb(f"{ROOT}/public/images/{VKEY[s]}.png") for s in VKEY}
    masks = {r: eroded_mask(r) for r in REGIONS}
    union = np.zeros((H, W), bool)
    for m in masks.values(): union |= m
    transfers = {}
    # The crevasse layers span two materials (snow shading above, rock below)
    # and their eroded mask is ~600px of thin veins, which collapses the
    # quantile transfer to two output colors and paints the trace window as a
    # flat slab at day/dusk/night. Build their transfer from the whole
    # mountain instead: dark inputs land in rock quantiles, light in snow,
    # and the window edges stay within a few units of the rock beneath them.
    mtn_mask = masks["crevasses"] | masks["mountain_rock"] | masks["snow_cap"]
    for s, img in variants.items():
        transfers[s] = {r: build_transfer(ref[masks[r]], img[masks[r]]) for r in REGIONS}
        transfers[s]["crevasses"] = build_transfer(ref[mtn_mask], img[mtn_mask])
        transfers[s]["__global__"] = build_transfer(ref[union], img[union])

    sky_full = cv2.imread(f"{ROOT}/parity/masks/sky.png", cv2.IMREAD_GRAYSCALE) > 127
    specials = json.load(open(f"{SP}/tokens.json"))["specials"]
    skyrows = json.load(open(f"{SP}/tokens.json"))["sky_base_rows"]

    # bird colors per state
    def bird_base(img, exclude=None):
        L = lum(img)
        rowmed = np.array([np.median(L[y][sky_full[y]]) if sky_full[y].sum() > 200 else 0
                           for y in range(H)])
        dark = sky_full & (L < rowmed[:, None] - 18)
        dark[int(H*0.55):] = False
        n, lab, stats, cent = cv2.connectedComponentsWithStats(dark.astype(np.uint8), 8)
        px = []
        for i in range(1, n):
            a = stats[i, cv2.CC_STAT_AREA]
            if not (8 <= a <= 900): continue
            cx, cy = cent[i]
            if exclude and np.hypot(cx-exclude[0], cy-exclude[1]) < exclude[2]*3.2: continue
            px.append(img[lab == i])
        if not px: return None
        allpx = np.concatenate(px)
        return tuple(np.median(allpx[:, i]) for i in range(3))
    moon = specials["night_moon"]
    bird = {"day": bird_base(variants["day"]),
            "dusk": bird_base(variants["dusk"]),
            "night": bird_base(variants["night"], (moon["cx"], moon["cy"], moon["r"]))}
    if bird["night"] is None:
        b = np.array(hex2rgb(skyrows["Night"]["0.2437"])) * 0.8
        bird["night"] = tuple(b)
    print("bird bases:", {k: rgb2hex(v) for k, v in bird.items()})

    T = Tokens()

    # region palettes for underpaint nearest-mapping
    segs = doc_segments(svg)
    region_pal = {}
    for name, seg in segs:
        if name in REGIONS:
            cols = set(c.lower() for c in re.findall(r'(?:fill|stroke)="(#[0-9a-fA-F]{6})"', seg))
            region_pal[name] = sorted(cols)
    lab_cache = {}
    def labof(h):
        if h not in lab_cache:
            lab_cache[h] = cv2.cvtColor(np.uint8([[hex2rgb(h)]]), cv2.COLOR_RGB2LAB)[0,0].astype(float)
        return lab_cache[h]
    def nearest_region(h):
        best, bd = None, 1e18
        for r, cols in region_pal.items():
            if r in ("sun_disc", "sun_ring"): continue
            for c in cols:
                d = np.sum((labof(c) - labof(h))**2)
                if d < bd: bd, best = d, r
        return best

    dawn_bird_levels = sorted(set(re.findall(r'fill="(#[0-9a-fA-F]{6})"', dict(segs)["birds"])),
                              key=lambda c: -lum(np.array(hex2rgb(c))))
    bird_mean_L = np.mean([lum(np.array(hex2rgb(c))) for c in dawn_bird_levels])

    try:
        OVR = json.load(open(f"{SP}/token_overrides.json"))
    except FileNotFoundError:
        OVR = {}

    def token_values(scope, dawnhex):
        """Fill T.vals for this token."""
        vals = {"dawn": dawnhex}
        for s in VKEY:
            ov = OVR.get(f"{scope}:{dawnhex}", {})
            if s in ov:
                vals[s] = ov[s]; continue
            man = MANUAL.get((scope, dawnhex), {})
            if s in man:
                vals[s] = man[s]; continue
            if scope == "birds":
                f = lum(np.array(hex2rgb(dawnhex))) / bird_mean_L
                vals[s] = rgb2hex(tuple(np.clip(np.array(bird[s]) * f, 0, 255)))
            elif scope in REGIONS or scope == "river_upper":
                # river_upper: same transfer as river (identical day/dusk),
                # it exists so token_overrides can retint the moonlit upper
                # valley at night without touching the foreground.
                r = "river" if scope == "river_upper" else scope
                vals[s] = rgb2hex(transfers[s][r](hex2rgb(dawnhex)))
            elif scope == "underpaint":
                r = nearest_region(dawnhex)
                vals[s] = rgb2hex(transfers[s][r](hex2rgb(dawnhex)))
            elif scope.startswith("skybase@"):
                off = scope.split("@")[1]
                vals[s] = skyrows[VKEY[s]][off]
            elif scope == "skyhaze":
                vals[s] = rgb2hex(transfers[s]["far_ridges"](hex2rgb(dawnhex)))
            else:
                vals[s] = rgb2hex(transfers[s]["__global__"](hex2rgb(dawnhex)))
        return vals

    SKIP_COLORS = {"#ffffff", "#000000"}  # sun_ring fade mask
    CONST_SCOPES = set()  # scopes whose colors stay dawn in all states

    def rewrite_tag(tag, scope, mode, state=None):
        """mode='artifact': add classes, keep dawn attrs. mode='bake': swap hexes."""
        classes = []
        def sub(attr, css):
            nonlocal tag, classes
            m = re.search(attr + r'="(#[0-9a-fA-F]{6})"', tag)
            if not m: return
            hexv = m.group(1).lower()
            if hexv in SKIP_COLORS and scope == "sun_ring": return
            if scope == "sky-warm":  # constant, fades via rect opacity
                return
            tid = T.get(scope, hexv)
            if tid not in T.vals:
                T.vals[tid] = token_values(scope, hexv)
            if mode == "artifact":
                classes.append(f"{css}{tid[1:]}")
            else:
                tag = tag[:m.start(1)] + T.vals[tid][state] + tag[m.end(1):]
        sub("fill", "f"); sub("stroke", "s"); sub("stop-color", "g")
        if mode == "artifact" and classes:
            i = tag.rfind("/>")
            if i == -1: i = tag.rfind(">")
            tag = tag[:i] + f' class="{" ".join(classes)}"' + tag[i:]
        return tag

    def rewrite_seg(name, seg, mode, state=None):
        scope = name
        out = []
        # inside sky group, defs gradients get their own scopes
        cur_grad = [None]
        def one(m):
            tag = m.group(0)
            gm = re.match(r'<(linearGradient|radialGradient)\b[^>]*id="([^"]+)"', tag)
            if gm:
                cur_grad[0] = gm.group(2); return tag
            if tag.startswith('</linearGradient') or tag.startswith('</radialGradient'):
                cur_grad[0] = None; return tag
            sc = scope
            if ' data-up=""' in tag:  # river subpath above the night lighting boundary
                tag = tag.replace(' data-up=""', '')
                sc = "river_upper"
            if cur_grad[0]:
                sc = {"sky-base": None, "sky-warm": "sky-warm", "sky-haze": "skyhaze",
                      "sun_disc-glow": "sun_disc", "river-flow": "river",
                      "sun_ring-fade": "sun_ring"}.get(cur_grad[0], scope)
                if cur_grad[0] == "sky-base":
                    om = re.search(r'offset="([\d.]+)"', tag)
                    off = str(float(om.group(1)))
                    sc = f"skybase@{off}"
            return rewrite_tag(tag, sc, mode, state)
        return re.sub(r'<[^>]+>', one, seg)

    def build(mode, state=None):
        parts = []
        for name, seg in segs:
            if name == "raw":
                parts.append(seg); continue
            if name == "topdefs":
                parts.append(rewrite_seg("topdefs", seg, mode, state)); continue
            if name == "crevasses":
                # One reference bird's body sat on the crevasse luminance levels
                # and traced into every crevasse path as a ~5px blob in open sky
                # (scene 1326,294). Birds are day-only via their own groups, so
                # strip the stray from all levels.
                def _strip_bird(mp):
                    subs = [s for s in re.findall(r'M[^M]+', mp.group(1))]
                    kept = []
                    for sub in subs:
                        sm = re.match(r'M\s*([\d.]+)[ ,]([\d.]+)', sub)
                        x, y = float(sm.group(1)), float(sm.group(2))
                        if 1320 <= x <= 1335 and 288 <= y <= 302:
                            _strip_bird.count += 1; continue
                        kept.append(sub)
                    return ' d="' + ''.join(kept) + '"'
                _strip_bird.count = 0
                seg = re.sub(r' d="([^"]+)"', _strip_bird, seg)
                assert _strip_bird.count >= 1, "stray crevasse bird not found"
            if name == "foreground_forest":
                # Anti-aliased pixels along the mountain's left snowline
                # clustered into the forest color levels and traced as ~5
                # speck subpaths at (568-650, 465-500), which relight green at
                # day: green dots on the snow. No legitimate forest exists
                # that high in the scene's center, so strip the zone.
                def _strip_ridge_specks(mp):
                    subs = re.findall(r'M[^M]+', mp.group(1))
                    kept = []
                    for sub in subs:
                        sm = re.match(r'M\s*([\d.]+)[ ,]([\d.]+)', sub)
                        x, y = float(sm.group(1)), float(sm.group(2))
                        if 400 < x < 1600 and y < 560:
                            _strip_ridge_specks.count += 1; continue
                        kept.append(sub)
                    return ' d="' + ''.join(kept) + '"'
                _strip_ridge_specks.count = 0
                seg = re.sub(r' d="([^"]+)"', _strip_ridge_specks, seg)
                assert _strip_ridge_specks.count == 5, \
                    f"expected 5 snowline specks, stripped {_strip_ridge_specks.count}"
            if name == "river":
                # Night's lighting boundary crosses the river at y963
                # (Night.png water medL 53.6 -> 21.4 between y960 and y966):
                # moonlit valley above, forest shadow below. The flat detail
                # layers span both, so subpaths starting above the boundary
                # move to marked twin paths scoped river_upper, whose night
                # values token_overrides.json pins to measured moonlit water.
                # All other states resolve river_upper identically to river.
                def _split_river(mp):
                    tag = mp.group(0)
                    dm = re.search(r' d="([^"]+)"', tag)
                    if not dm: return tag
                    ups, los = [], []
                    for sub in re.findall(r'M[^M]+', dm.group(1)):
                        sy = float(re.match(r'M\s*[\d.]+[ ,]([\d.]+)', sub).group(1))
                        (ups if sy < 963 else los).append(sub)
                    if not ups: return tag
                    _split_river.count += len(ups)
                    up_tag = (tag[:dm.start(1)] + ''.join(ups) + tag[dm.end(1):]
                              ).replace('<path', '<path data-up=""', 1)
                    if not los: return up_tag
                    return tag[:dm.start(1)] + ''.join(los) + tag[dm.end(1):] + up_tag
                _split_river.count = 0
                seg = re.sub(r'<path[^>]*/>', _split_river, seg)
                assert _split_river.count > 100, \
                    f"river split found only {_split_river.count} upper subpaths"
            if name == "underpaint":
                # The birds' underpaint blob must hide with the birds (day
                # only), or ghost chevrons show through at dawn/dusk/night.
                bm = re.search(r'<path[^>]*fill="#cfafa7"[^>]*/>', seg)
                assert bm and seg.count('fill="#cfafa7"') == 1, "birds underpaint moved"
                seg = (seg[:bm.start()] + hooked_open("birds_under", mode, state)
                       + bm.group(0) + "</g>" + seg[bm.end():])
            body = rewrite_seg(name, seg, mode, state)
            if name == "sky":
                # id the warm rect; append stars group after sky
                wop = GROUP_STATE["sky_warm_rect"][state] if mode == "bake" else 1
                wattr = ' id="sky_warm_rect"' + (f' opacity="{wop}"' if wop != 1 else "")
                body = body.replace('<rect x="0" y="0" width="2028" height="1108" fill="url(#sky-warm)"/>',
                                    f'<rect x="0" y="0" width="2028" height="1108" fill="url(#sky-warm)"{wattr}/>')
                cut = body.rfind("</g>")
                body = body[:cut] + hooked_group("dusk_sky_lr", mode, state) + body[cut:]
                body += "\n" + hooked_group("stars", mode, state)
            if name == "sun_ring":
                # open sun_travel wrapper (day halo first)
                halo = ('<radialGradient id="day_halo-g" gradientUnits="userSpaceOnUse" cx="1013" cy="209" r="520">'
                        '<stop offset="0" stop-color="#ffffff" stop-opacity="0.50"/>'
                        '<stop offset="0.12" stop-color="#fdf8e6" stop-opacity="0.20"/>'
                        '<stop offset="0.35" stop-color="#eef4fb" stop-opacity="0.05"/>'
                        '<stop offset="0.8" stop-color="#eef4fb" stop-opacity="0"/>'
                        '<stop offset="1" stop-color="#eef4fb" stop-opacity="0"/></radialGradient>')
                open_travel = hooked_open("sun_travel", mode, state, transform=True)
                dayhalo = (f'<defs>{halo}</defs>' +
                           hooked_open("day_halo", mode, state) +
                           '<circle cx="1013" cy="209" r="520" fill="url(#day_halo-g)"/></g>')
                body = open_travel + dayhalo + inject_group_state(body, "sun_ring", mode, state)
            if name == "birds":
                body = inject_group_state(body, "birds", mode, state)
            if name == "sun_disc":
                body = body + "\n</g>"  # close sun_travel
            if name == "crevasses":
                body += "\n" + hooked_group("dusk_rim", mode, state) + "\n" + hooked_group("moon", mode, state)
                # A dead-straight crack at (575-607, 610-617) - a hole shared
                # by the traced rock shapes AND dusk_rim's field - exposes
                # far_ridges:#8d97b0 beneath: invisible at dawn (the rock
                # around it is the same #8d97b0) but a salmon dash at dusk
                # because far_ridges relights warmer. Capsule patch above the
                # rim field; its own ridge_patch scope gets per-state values
                # pinned in token_overrides.json to the surrounding composite
                # (rock at day/night, the rim field color at dusk).
                patch = '<rect x="573" y="609" width="37" height="9" rx="4.5" fill="#8d97b0"/>'
                body += rewrite_seg("ridge_patch", patch, mode, state)
            if name == "mid_ridges":
                # The traced ridge band tops out dead flat at y~705 for
                # hundreds of px (the trace window's edge). At dawn the step
                # across it is soft (sum|d|~17) but rock above and ridges
                # below relight through different transfers, tripling the
                # step at day. A soft elliptical haze in the rock's own dawn
                # color (#7d89a9, measured at y694-700 x450-1550), scoped
                # mountain_rock so it tracks the tone above the seam in every
                # state, feathers the boundary back to ~dawn softness. The
                # ellipse reaches alpha 0 exactly at the rect's edges, so the
                # rect adds no edges of its own.
                haze = ('<defs><radialGradient id="ridge-haze" gradientUnits="userSpaceOnUse" '
                        'cx="0" cy="0" r="1" gradientTransform="translate(1010 705) scale(660 30)">'
                        '<stop offset="0" stop-color="#7d89a9" stop-opacity="0.6"/>'
                        '<stop offset="0.45" stop-color="#7d89a9" stop-opacity="0.6"/>'
                        '<stop offset="0.75" stop-color="#7d89a9" stop-opacity="0.3"/>'
                        '<stop offset="1" stop-color="#7d89a9" stop-opacity="0"/></radialGradient></defs>'
                        '<rect x="350" y="675" width="1320" height="60" fill="url(#ridge-haze)"/>')
                body += rewrite_seg("mountain_rock", haze, mode, state)
                body += "\n" + hooked_group("dusk_horizon", mode, state)
            if name == "pipe_smoke":
                body += "\n" + hooked_group("dusk_front", mode, state) + "\n" + hooked_group("night_fx", mode, state)
            parts.append(body)
        return "".join(parts)

    overlays = {}
    try:
        overlays = json.load(open(f"{SP}/overlays.json"))
    except FileNotFoundError:
        pass

    def hooked_open(gid, mode, state, transform=False):
        if mode == "artifact":
            return f'<g id="{gid}">'
        op = GROUP_STATE[gid][state]
        tt = TRANSFORMS.get(gid)
        t = f' transform="{tt[state]}"' if tt else ""
        o = f' opacity="{op}"' if op != 1 else ""
        return f'<g id="{gid}"{t}{o}>'

    def hooked_group(gid, mode, state):
        content = overlays.get(gid, "")
        return hooked_open(gid, mode, state) + content + "</g>"

    def inject_group_state(body, gid, mode, state):
        if mode == "artifact": return body
        op = GROUP_STATE[gid][state]
        if op == 1: return body
        return body.replace(f'<g id="{gid}"', f'<g id="{gid}" opacity="{op}"', 1)

    # --- artifact pass (also populates token table) ---
    art_svg = build("artifact")

    # --- CSS ---
    props, dawn_decl, state_decl, classes, translist = [], [], {s: [] for s in VKEY}, [], []
    for (scope, hexv), tid in T.bykey.items():
        v = T.vals[tid]
        props.append(f"@property --{tid}{{syntax:'<color>';inherits:true;initial-value:{v['dawn']};}}")
        dawn_decl.append(f"--{tid}:{v['dawn']};")
        for s in VKEY:
            if v[s] != v["dawn"]:
                state_decl[s].append(f"--{tid}:{v[s]};")
        translist.append(f"--{tid} var(--t-sky)")
    used = set()
    for (scope, hexv), tid in T.bykey.items():
        used.add(tid)
    # class rules
    cls_rules = []
    for (scope, hexv), tid in T.bykey.items():
        n = tid[1:]
        cls_rules.append(f".f{n}{{fill:var(--{tid});}}")
        cls_rules.append(f".s{n}{{stroke:var(--{tid});}}")
        cls_rules.append(f".g{n}{{stop-color:var(--{tid});}}")
    # only emit rules actually referenced
    used_cls = set(re.findall(r'class="([^"]+)"', art_svg))
    flat = set(c for group in used_cls for c in group.split())
    cls_rules = [r for r in cls_rules if r[1:r.index("{")] in flat]

    gs_css = []
    for gid, ops in GROUP_STATE.items():
        base_op = ops["dawn"]
        tt = TRANSFORMS.get(gid)
        extra = f"transform:{css_t(tt['dawn'])};" if tt else ""
        base_trans = "transition:opacity var(--t-sky),transform var(--t-sky);"
        if gid == "sun_travel":
            # arriving at a sun-visible state: fade in while the movement runs
            base_trans = "transition:opacity 1.2s ease,transform var(--t-sky);"
        gs_css.append(f"#{gid}{{opacity:{base_op};{extra}{base_trans}}}")
        for s in STATES:
            if s == "dawn": continue
            decl = f"opacity:{ops[s]};"
            if tt:
                decl += f"transform:{css_t(tt[s])};"
            if gid == "sun_travel" and s in ("dusk", "night"):
                # hold full opacity through the travel, fade only after arrival
                decl += "transition:transform var(--t-sky),opacity 0.9s ease var(--t-sky);"
            gs_css.append(f'html[data-time="{s}"] #{gid}{{{decl}}}')

    css = f"""
:root{{--t-sky:2.4s;}}
{chr(10).join(props)}
html{{{"".join(dawn_decl)}}}
html{{transition:{",".join(translist)};}}
html[data-time="day"]{{{"".join(state_decl["day"])}}}
html[data-time="dusk"]{{{"".join(state_decl["dusk"])}}}
html[data-time="night"]{{{"".join(state_decl["night"])}}}
{chr(10).join(cls_rules)}
{chr(10).join(gs_css)}
@media (prefers-reduced-motion: reduce){{html,{",".join("#" + g for g in GROUP_STATE)}{{transition:none;}}}}
html,body{{margin:0;height:100%;background:#0c1c24;}}
.skyfield{{position:fixed;inset:0;}}
.skyfield svg{{width:100%;height:100%;display:block;}}
.hud{{position:fixed;right:18px;bottom:14px;display:flex;gap:14px;z-index:2;
 font:500 11px/1 -apple-system,'Segoe UI',sans-serif;letter-spacing:0.22em;}}
.hud button{{all:unset;cursor:pointer;color:rgba(255,255,255,0.55);padding:6px 2px;}}
.hud button:hover{{color:rgba(255,255,255,0.9);}}
.hud button[aria-pressed="true"]{{color:#ffd9a0;border-bottom:1px solid #ffd9a0;}}
"""
    js = """
const hud=document.querySelector('.hud');
function bucket(){const h=new Date().getHours();
 return h>=5&&h<8?'dawn':h>=8&&h<17?'day':h>=17&&h<21?'dusk':'night';}
let mode=localStorage.getItem('sf-time')||'auto';
function apply(){const t=mode==='auto'?bucket():mode;
 document.documentElement.dataset.time=t;
 hud.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.m===mode));}
hud.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;
 mode=b.dataset.m;localStorage.setItem('sf-time',mode);apply();});
apply();setInterval(()=>{if(mode==='auto')apply();},60000);
"""
    html = f"""
<title>Skyfield</title>
<style>{css}</style>
<div class="skyfield">
{art_svg}
</div>
<div class="hud">
<button data-m="dawn">DAWN</button><button data-m="day">DAY</button><button data-m="dusk">DUSK</button><button data-m="night">NIGHT</button><button data-m="auto">AUTO</button>
</div>
<script>{js}</script>
"""
    open(f"{SP}/artifact.html", "w").write(html)

    # --- baked passes ---
    for s in STATES:
        baked = build("bake", s)
        open(f"{SP}/baked_{s}.svg", "w").write(baked)

    print(f"tokens: {len(T.bykey)}  artifact: {len(html)} bytes")
    # dump token table for inspection
    json.dump({f"{sc}:{hx}": T.vals[tid] for (sc, hx), tid in T.bykey.items()},
              open(f"{SP}/token_table.json", "w"), indent=1)

if __name__ == "__main__":
    main()
