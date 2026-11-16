"""Generate the animated SVG assets for the GitHub profile README.

Everything is hand-built SVG (no third-party card services), so the profile
renders the same for every viewer and never hits a rate limit. Palette and
type follow https://aarush.work (slate #0f172a, cyan #38bdf8).

Run:  python3 scripts/build_assets.py
"""

import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

BG, BG_ALT, BORDER = "#0f172a", "#1e293b", "#2d3b52"
ACCENT, ACCENT_DEEP = "#38bdf8", "#0ea5e9"
HEADING, TEXT, MUTED = "#e2e8f0", "#cbd5e1", "#94a3b8"
INDIGO, AMBER, ROSE = "#818cf8", "#fbbf24", "#fb7185"

DISPLAY = "'Space Grotesk','Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif"
BODY = "'Inter','Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def starfield(rng, w, h, n, twinkle_ratio=0.25):
    tints = ["#ffffff", "#e0f2fe", "#bae6fd", "#c7d2fe"]
    out = []
    for _ in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        r = rng.choice([0.5, 0.6, 0.7, 0.8, 1.0, 1.2, 1.5])
        op = rng.uniform(0.25, 0.85)
        fill = rng.choice(tints)
        if rng.random() < twinkle_ratio:
            d = rng.uniform(2.5, 6.0)
            delay = rng.uniform(0, 6)
            out.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" opacity="{op:.2f}" '
                f'class="tw" style="animation-duration:{d:.1f}s;animation-delay:-{delay:.1f}s"/>'
            )
        else:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" opacity="{op:.2f}"/>')
    return "\n    ".join(out)


LOGOS = Path(__file__).resolve().parent.parent / "assets" / "logos"


def logo_tile(name, x, y, size):
    """Logo drawn inside a white tile. External images never load inside a
    README SVG, so the Amazon mark is inlined as a vector and the Biosphere 2
    mark as base64 PNG."""
    import base64, re
    pad = size * 0.16
    inner = size - 2 * pad
    if name == "amazon":
        d = re.search(r' d="([^"]+)"', (LOGOS / "amazon.svg").read_text()).group(1)
        k = inner / 24
        # one path in the source: split it so the letter is ink and the smile is orange
        return (
            f'<clipPath id="amzTop"><rect x="0" y="0" width="24" height="16.9"/></clipPath>'
            f'<clipPath id="amzBot"><rect x="0" y="16.9" width="24" height="8"/></clipPath>'
            f'<g transform="translate({x+pad:.1f},{y+pad:.1f}) scale({k:.4f})">'
            f'<path d="{d}" fill="#232f3e" clip-path="url(#amzTop)"/>'
            f'<path d="{d}" fill="#ff9900" clip-path="url(#amzBot)"/></g>'
        )
    b64 = base64.b64encode((LOGOS / f"{name}.png").read_bytes()).decode()
    return (
        f'<image x="{x+pad:.1f}" y="{y+pad:.1f}" width="{inner:.1f}" height="{inner:.1f}" '
        f'preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{b64}"/>'
    )


def moon_svg(x, y, r):
    """The portfolio's hero moon: a real lunar photo clipped to a disc with a
    soft cool halo. Photo: Gregory H. Revera, CC BY-SA 3.0 (credited in the
    SVG's <desc>). Embedded as base64 because README SVGs cannot load URLs."""
    import base64
    b64 = base64.b64encode((LOGOS / "moon.jpg").read_bytes()).decode()
    o = r * 0.04  # slight overscan so the photo edge meets the clip cleanly
    return f'''<radialGradient id="moonHalo" gradientUnits="userSpaceOnUse" cx="{x}" cy="{y}" r="{r*2.1:.1f}">
      <stop offset="{0.85/2.1:.3f}" stop-color="rgb(186,210,245)" stop-opacity="0.16"/>
      <stop offset="1" stop-color="rgb(186,210,245)" stop-opacity="0"/></radialGradient>
    <radialGradient id="moonLimb" gradientUnits="userSpaceOnUse" cx="{x - r*0.25:.1f}" cy="{y - r*0.25:.1f}" r="{r*1.35:.1f}">
      <stop offset="0.55" stop-color="#0b1020" stop-opacity="0"/>
      <stop offset="1" stop-color="#0b1020" stop-opacity="0.55"/></radialGradient>
    <clipPath id="moonClip"><circle cx="{x}" cy="{y}" r="{r}"/></clipPath>
    <circle cx="{x}" cy="{y}" r="{r*2.1:.1f}" fill="url(#moonHalo)" class="halo"/>
    <g clip-path="url(#moonClip)">
      <image x="{x-r-o:.1f}" y="{y-r-o:.1f}" width="{2*(r+o):.1f}" height="{2*(r+o):.1f}" href="data:image/jpeg;base64,{b64}"/>
      <circle cx="{x}" cy="{y}" r="{r}" fill="url(#moonLimb)"/>
    </g>
    <desc>Moon photo: Gregory H. Revera, CC BY-SA 3.0</desc>'''


# --------------------------------------------------------------------------- hero
def hero():
    W, H = 1200, 510
    hl_y, chip_y = 338, 422
    # moon, after the hero moon on aarush.work (top right, cool halo)
    mx, my, mr = 1078, 142, 60
    rng = random.Random(7)
    stars = starfield(rng, W, H, 170)

    # Typed role line, same rotation as the portfolio hero.
    roles = [
        "production AI systems.",
        "computer vision models.",
        "Gen AI copilots.",
        "ML pipelines.",
        "data-driven solutions.",
    ]
    fs, cw = 24, 14.4  # mono font size and forced per-char advance (textLength)
    x0, y0 = 64, 302
    prefix = "I build "
    px = x0 + len(prefix) * cw
    slot, t_type, t_hold, t_erase = 3.8, 1.3, 1.9, 0.45
    cycle = slot * len(roles)

    def keyframes(points):
        """[(t_seconds, value)] -> (keyTimes, values) strings, deduping equal times."""
        out = []
        for t, v in sorted(points, key=lambda p: p[0]):
            if out and abs(out[-1][0] - t) < 1e-9:
                out[-1] = (t, v)
            else:
                out.append((t, v))
        return (";".join(f"{t/cycle:.4f}" for t, _ in out), ";".join(f"{v:.1f}" for _, v in out))

    clips, texts, cursor_pts = [], [], [(0, px), (cycle, px)]
    for i, role in enumerate(roles):
        wid = len(role) * cw + 2
        s = i * slot
        pts = [(s, 0), (s + t_type, wid), (s + t_type + t_hold, wid), (s + t_type + t_hold + t_erase, 0)]
        kt, vals = keyframes([(0, 0), (cycle, 0)] + pts)
        clips.append(
            f'''<clipPath id="c{i}"><rect x="{px}" y="{y0-26}" height="36" width="0">
      <animate attributeName="width" dur="{cycle}s" repeatCount="indefinite" keyTimes="{kt}" values="{vals}"/></rect></clipPath>'''
        )
        texts.append(
            f'''<text x="{px}" y="{y0}" clip-path="url(#c{i})" textLength="{len(role)*cw:.1f}" lengthAdjust="spacingAndGlyphs"
    font-family="{MONO}" font-size="{fs}" fill="url(#accentGrad)">{esc(role)}</text>'''
        )
        cursor_pts += [(t, px + v) for t, v in pts]
    ckt, cvals = keyframes(cursor_pts)

    # Constellation that doubles as a small neural net.
    layers = [3, 5, 5, 3, 1]
    nx0, nx1, ny0, ny1 = 650, 950, 92, 302
    nodes = []
    for li, n in enumerate(layers):
        x = nx0 + (nx1 - nx0) * li / (len(layers) - 1)
        for j in range(n):
            y = (ny0 + ny1) / 2 + (j - (n - 1) / 2) * ((ny1 - ny0) / 5)
            y += rng.uniform(-9, 9)
            nodes.append((li, x + rng.uniform(-8, 8), y))
    edges = []
    for a in nodes:
        for b in nodes:
            if b[0] == a[0] + 1:
                edges.append((a, b))
    edge_svg = "\n    ".join(
        f'<line x1="{a[1]:.1f}" y1="{a[2]:.1f}" x2="{b[1]:.1f}" y2="{b[2]:.1f}"/>' for a, b in edges
    )
    pulse_edges = rng.sample(edges, 16)
    pulses = []
    for k, (a, b) in enumerate(pulse_edges):
        dur = rng.uniform(2.2, 3.6)
        beg = rng.uniform(0, 4)
        pulses.append(
            f'''<circle r="2.2" fill="{ACCENT}" filter="url(#glow)">
      <animateMotion dur="{dur:.2f}s" begin="-{beg:.2f}s" repeatCount="indefinite"
        path="M{a[1]:.1f},{a[2]:.1f} L{b[1]:.1f},{b[2]:.1f}"/>
      <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.15;0.8;1" dur="{dur:.2f}s" begin="-{beg:.2f}s" repeatCount="indefinite"/>
    </circle>'''
        )
    node_svg = "\n    ".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{4.2 if li in (0, len(layers)-1) else 3.4}" '
        f'class="node" style="animation-delay:-{(li*0.6 + y/90):.2f}s"/>'
        for li, x, y in nodes
    )

    chips = [
        "MS Data Science · University of Arizona",
        "Tucson, AZ",
        "DEXA 2024 · Springer LNCS",
        "prev. HCL Technologies · PwC · Carrier",
    ]
    cx, chip_svg = 64, []
    for c in chips:
        tw = len(c) * 7.3
        chip_svg.append(
            f'<rect x="{cx}" y="{chip_y}" width="{tw+26:.1f}" height="30" rx="15" fill="{BG_ALT}" fill-opacity="0.7" stroke="{BORDER}"/>'
            f'<text x="{cx+13}" y="{chip_y+20}" textLength="{tw:.1f}" lengthAdjust="spacingAndGlyphs" font-family="{BODY}" font-size="13" fill="{TEXT}">{esc(c)}</text>'
        )
        cx += tw + 26 + 10

    # Current highlights, each with its organisation's logo on a light tile.
    highlights = [
        ("amazon", "Amazon · Eller Immersion Project", "Weather driven delivery capacity forecasting"),
        ("biosphere2", "Biosphere 2 · AI/ML & Software Engineer", "Sensor data quality and edge telemetry"),
    ]
    hx, hl_svg = 64, []
    for i, (logo, title, sub) in enumerate(highlights):
        tw_t, tw_s = len(title) * 8.1, len(sub) * 6.6
        cw_ = 66 + max(tw_t, tw_s) + 78
        hl_svg.append(
            f'<g class="rise" style="animation-delay:{0.25 + i*0.15:.2f}s">'
            f'<rect x="{hx}" y="{hl_y}" width="{cw_:.1f}" height="60" rx="14" fill="{BG_ALT}" fill-opacity="0.82" stroke="url(#hlStroke)"/>'
            f'<rect x="{hx+9}" y="{hl_y+9}" width="42" height="42" rx="10" fill="#ffffff"/>'
            f'{logo_tile(logo, hx+9, hl_y+9, 42)}'
            f'<text x="{hx+64}" y="{hl_y+26}" textLength="{tw_t:.1f}" lengthAdjust="spacingAndGlyphs" font-family="{DISPLAY}" font-size="15" font-weight="600" fill="{HEADING}">{esc(title)}</text>'
            f'<text x="{hx+64}" y="{hl_y+45}" textLength="{tw_s:.1f}" lengthAdjust="spacingAndGlyphs" font-family="{BODY}" font-size="12" fill="{MUTED}">{esc(sub)}</text>'
            f'<circle cx="{hx+cw_-56:.1f}" cy="{hl_y+30}" r="3.5" fill="#34d399" class="live"/>'
            f'<text x="{hx+cw_-47:.1f}" y="{hl_y+34}" font-family="{MONO}" font-size="10.5" letter-spacing="1.5" fill="#34d399">NOW</text>'
            f'</g>'
        )
        hx += cw_ + 14

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Aarush Narang, Data Scientist and ML Engineer">
  <title>Aarush Narang · Data Scientist &amp; ML Engineer</title>
  <defs>
    <radialGradient id="glowA" cx="85%" cy="10%" r="60%"><stop offset="0" stop-color="#6366f1" stop-opacity="0.22"/><stop offset="1" stop-color="#6366f1" stop-opacity="0"/></radialGradient>
    <radialGradient id="glowB" cx="5%" cy="100%" r="55%"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0.16"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient>
    <linearGradient id="nameGrad" x1="0" x2="1"><stop offset="0" stop-color="{HEADING}"/><stop offset="0.55" stop-color="#f8fafc"/><stop offset="1" stop-color="{ACCENT}"/></linearGradient>
    <linearGradient id="accentGrad" x1="0" x2="1"><stop offset="0" stop-color="{ACCENT}"/><stop offset="1" stop-color="{INDIGO}"/></linearGradient>
    <linearGradient id="shoot" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="0.9"/></linearGradient>
    <filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <linearGradient id="hlStroke" x1="0" x2="1"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0.55"/><stop offset="1" stop-color="{BORDER}"/></linearGradient>
    <clipPath id="frame"><rect width="{W}" height="{H}" rx="20"/></clipPath>
    {''.join(clips)}
  </defs>
  <style>
    .tw {{ animation-name: tw; animation-iteration-count: infinite; animation-timing-function: ease-in-out; }}
    @keyframes tw {{ 0%,100% {{ opacity: .15 }} 50% {{ opacity: 1 }} }}
    .node {{ fill: {BG}; stroke: {ACCENT}; stroke-width: 1.6; animation: node 3.2s ease-in-out infinite; }}
    @keyframes node {{ 0%,100% {{ stroke-opacity: .45 }} 50% {{ stroke-opacity: 1 }} }}
    .shoot {{ animation: shoot 9s linear infinite; }}
    @keyframes shoot {{ 0% {{ transform: translate(0,0); opacity: 0 }} 2% {{ opacity: 1 }} 9% {{ transform: translate(460px,170px); opacity: 0 }} 100% {{ transform: translate(460px,170px); opacity: 0 }} }}
    .blink {{ animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0 }} }}
    .rise {{ animation: rise 1.1s cubic-bezier(.22,1,.36,1) both; }}
    @keyframes rise {{ from {{ transform: translateY(14px) }} to {{ transform: none }} }}
    .live {{ animation: live 2s ease-in-out infinite; }}
    .halo {{ animation: halo 7s ease-in-out infinite; }}
    @keyframes halo {{ 0%,100% {{ opacity: .75 }} 50% {{ opacity: 1 }} }}
    @keyframes live {{ 0%,100% {{ opacity: 1 }} 50% {{ opacity: .3 }} }}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
  </style>
  <g clip-path="url(#frame)">
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <rect width="{W}" height="{H}" fill="url(#glowA)"/>
    <rect width="{W}" height="{H}" fill="url(#glowB)"/>
    {stars}
    <g class="shoot"><line x1="250" y1="-10" x2="360" y2="31" stroke="url(#shoot)" stroke-width="1.6" stroke-linecap="round"/></g>
    <g stroke="{ACCENT}" stroke-opacity="0.13" stroke-width="1">
    {edge_svg}
    </g>
    {''.join(pulses)}
    {node_svg}
    {moon_svg(mx, my, mr)}
    <text x="{W-40}" y="{H-24}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}" letter-spacing="2">PERCEIVE · RETRIEVE · REASON · SHIP</text>
  </g>
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="20" fill="none" stroke="{BORDER}"/>

  <g class="rise">
    <text x="{x0}" y="114" font-family="{MONO}" font-size="15" fill="{ACCENT}" fill-opacity="0.85">~/aarush <tspan fill="{MUTED}">$</tspan> whoami</text>
    <text x="{x0-3}" y="196" font-family="{DISPLAY}" font-size="72" font-weight="700" letter-spacing="-1.5" fill="url(#nameGrad)">Aarush Narang</text>
    <text x="{x0}" y="240" font-family="{DISPLAY}" font-size="25" font-weight="500" fill="{TEXT}">Data Scientist &amp; ML Engineer</text>
  </g>
  <text x="{x0}" y="{y0}" textLength="{len(prefix)*cw - cw*0.4:.1f}" lengthAdjust="spacingAndGlyphs" font-family="{MONO}" font-size="{fs}" fill="{MUTED}">I build</text>
  {''.join(texts)}
  <g class="blink"><rect x="{px}" y="{y0-21}" width="11" height="26" rx="1.5" fill="{ACCENT}">
    <animate attributeName="x" dur="{cycle}s" repeatCount="indefinite"
      keyTimes="{ckt}" values="{cvals}"/></rect></g>
  {''.join(hl_svg)}
  {''.join(chip_svg)}
</svg>'''
    (OUT / "hero.svg").write_text(svg)


# ------------------------------------------------------------------------ impact
def impact():
    W, H = 1200, 270
    tiles = [
        ("89%", "top 5 retrieval hit rate", "RAG over 4,000+ docs · up from 74%", ("delta", 74, 89, 100)),
        ("−26%", "daily service desk tickets", "2,300 → 1,700 tickets per day", ("pair", 2300, 1700)),
        ("94%", "MCP tool selection accuracy", "120 golden evaluation tasks", ("delta", 0, 94, 100)),
        ("−76%", "incident resolution time", "105 → 25 minutes", ("pair", 105, 25)),
    ]
    tw, gap, mx, ty = 270, 20, 25, 62
    parts = []
    for i, (big, label, sub, viz) in enumerate(tiles):
        x = mx + i * (tw + gap)
        d = 0.15 * i
        parts.append(
            f'<g class="tile" style="animation-delay:{d:.2f}s">'
            f'<rect x="{x}" y="{ty}" width="{tw}" height="180" rx="14" fill="{BG_ALT}" fill-opacity="0.75" stroke="{BORDER}"/>'
            f'<text x="{x+22}" y="{ty+62}" font-family="{DISPLAY}" font-size="46" font-weight="700" fill="url(#ag)">{big}</text>'
            f'<text x="{x+22}" y="{ty+92}" font-family="{BODY}" font-size="15" font-weight="600" fill="{HEADING}">{esc(label)}</text>'
            f'<text x="{x+22}" y="{ty+114}" font-family="{BODY}" font-size="12.5" fill="{MUTED}">{esc(sub)}</text>'
        )
        bx, bw, by = x + 22, tw - 44, ty + 136
        if viz[0] == "delta":
            _, a, b, top = viz
            parts.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="10" rx="5" fill="{BG}"/>')
            if a:
                parts.append(f'<rect x="{bx}" y="{by}" width="{bw*a/top:.1f}" height="10" rx="5" fill="{MUTED}" fill-opacity="0.45"/>')
            parts.append(
                f'<rect x="{bx + bw*a/top:.1f}" y="{by}" width="{bw*(b-a)/top:.1f}" height="10" rx="5" fill="url(#ag)" class="grow" style="animation-delay:{0.5+d:.2f}s"/>'
            )
            parts.append(f'<text x="{bx}" y="{by+28}" font-family="{MONO}" font-size="11" fill="{MUTED}">0</text>')
            parts.append(f'<text x="{bx+bw}" y="{by+28}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">100</text>')
        else:
            _, a, b = viz
            parts.append(f'<rect x="{bx}" y="{by-4}" width="{bw}" height="8" rx="4" fill="{MUTED}" fill-opacity="0.4"/>')
            parts.append(
                f'<rect x="{bx}" y="{by+12}" width="{bw*b/a:.1f}" height="8" rx="4" fill="url(#ag)" class="grow" style="animation-delay:{0.5+d:.2f}s"/>'
            )
            parts.append(f'<text x="{bx}" y="{by+38}" font-family="{MONO}" font-size="11" fill="{MUTED}">before · after</text>')
        parts.append("</g>")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Production ML impact at HCL Technologies">
  <title>Production ML impact · HCL Technologies</title>
  <defs><linearGradient id="ag" x1="0" x2="1"><stop offset="0" stop-color="{ACCENT}"/><stop offset="1" stop-color="{INDIGO}"/></linearGradient></defs>
  <style>
    .tile {{ animation: rise .9s cubic-bezier(.22,1,.36,1) both; }}
    @keyframes rise {{ from {{ transform: translateY(12px) }} to {{ transform: none }} }}
    .grow {{ transform-box: fill-box; transform-origin: left center; animation: grow 1.4s cubic-bezier(.22,1,.36,1) both; }}
    @keyframes grow {{ from {{ transform: scaleX(0) }} to {{ transform: scaleX(1) }} }}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
  </style>
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="20" fill="{BG}" stroke="{BORDER}"/>
  <text x="{mx}" y="40" font-family="{MONO}" font-size="13" letter-spacing="2.5" fill="{ACCENT}">PRODUCTION ML <tspan fill="{MUTED}">· HCL TECHNOLOGIES · GENERATIVE AI TEAM · 2024–2025</tspan></text>
  {''.join(parts)}
</svg>'''
    (OUT / "impact.svg").write_text(svg)


# ---------------------------------------------------------------- project cards
def card_frame(W, H, title, tagline, metrics, stack, scene, label, extra_style=""):
    mparts = []
    mw = (W - 48 - 2 * 12) / 3
    for i, (big, small) in enumerate(metrics):
        x = 24 + i * (mw + 12)
        mparts.append(
            f'<rect x="{x:.1f}" y="262" width="{mw:.1f}" height="64" rx="10" fill="{BG}" stroke="{BORDER}"/>'
            f'<text x="{x+14:.1f}" y="292" font-family="{DISPLAY}" font-size="22" font-weight="700" fill="url(#ag)">{esc(big)}</text>'
            f'<text x="{x+14:.1f}" y="313" font-family="{BODY}" font-size="11.5" fill="{MUTED}">{esc(small)}</text>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}: {esc(tagline)}">
  <title>{esc(title)} · {esc(tagline)}</title>
  <defs>
    <linearGradient id="ag" x1="0" x2="1"><stop offset="0" stop-color="{ACCENT}"/><stop offset="1" stop-color="{INDIGO}"/></linearGradient>
    <clipPath id="sc"><rect x="16" y="16" width="{W-32}" height="150" rx="12"/></clipPath>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
  </defs>
  <style>
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
    {extra_style}
  </style>
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="{BG_ALT}" stroke="{BORDER}"/>
  <g clip-path="url(#sc)">{scene}</g>
  <rect x="16.5" y="16.5" width="{W-33}" height="149" rx="12" fill="none" stroke="{BORDER}"/>
  <text x="{W-24}" y="204" text-anchor="end" font-family="{MONO}" font-size="10.5" letter-spacing="1.5" fill="{MUTED}">{esc(label)}</text>
  <text x="24" y="206" font-family="{DISPLAY}" font-size="28" font-weight="700" fill="{HEADING}">{esc(title)}</text>
  <text x="24" y="234" font-family="{BODY}" font-size="14" fill="{TEXT}">{esc(tagline)}</text>
  {''.join(mparts)}
  <text x="24" y="356" font-family="{MONO}" font-size="11" fill="{ACCENT}" fill-opacity="0.85">{esc(stack)}</text>
</svg>'''


def reflex():
    W, H = 590, 376
    # top-down intersection, two tracked road users converging
    scene = f'''
    <rect x="16" y="16" width="{W-32}" height="150" fill="#0b1222"/>
    <rect x="16" y="66" width="{W-32}" height="52" fill="#131d33"/>
    <rect x="300" y="16" width="64" height="150" fill="#131d33"/>
    <g stroke="{MUTED}" stroke-opacity="0.35" stroke-dasharray="10 9" stroke-width="1.4">
      <line x1="16" y1="92" x2="300" y2="92"/><line x1="364" y1="92" x2="{W-16}" y2="92"/>
      <line x1="332" y1="16" x2="332" y2="66"/><line x1="332" y1="118" x2="332" y2="166"/>
    </g>
    <g fill="{MUTED}" fill-opacity="0.25">
      {''.join(f'<rect x="{300+k*9}" y="54" width="5" height="10"/>' for k in range(7))}
      {''.join(f'<rect x="{300+k*9}" y="120" width="5" height="10"/>' for k in range(7))}
    </g>
    <path d="M40,80 C150,80 240,80 330,80" stroke="{ACCENT}" stroke-opacity="0.35" stroke-width="1.5" fill="none" stroke-dasharray="3 5"/>
    <path d="M348,24 C348,60 348,70 348,104" stroke="{AMBER}" stroke-opacity="0.4" stroke-width="1.5" fill="none" stroke-dasharray="3 5"/>
    <g class="carA">
      <rect x="0" y="0" width="38" height="20" rx="4" fill="{ACCENT}" fill-opacity="0.22"/>
      <rect x="-4" y="-4" width="46" height="28" fill="none" stroke="{ACCENT}" stroke-width="1.5"/>
      <rect x="-4" y="-17" width="56" height="13" fill="{ACCENT}"/>
      <text x="0" y="-7" font-family="{MONO}" font-size="9" font-weight="700" fill="{BG}">car #12</text>
    </g>
    <g class="bike">
      <rect x="0" y="0" width="12" height="22" rx="3" fill="{AMBER}" fill-opacity="0.25"/>
      <rect x="-4" y="-4" width="20" height="30" fill="none" stroke="{AMBER}" stroke-width="1.5"/>
      <rect x="18" y="-4" width="62" height="13" fill="{AMBER}"/>
      <text x="22" y="6" font-family="{MONO}" font-size="9" font-weight="700" fill="{BG}">cyclist #7</text>
    </g>
    <g class="alert">
      <circle cx="342" cy="84" r="22" fill="none" stroke="{ROSE}" stroke-width="2"/>
      <circle cx="342" cy="84" r="22" fill="{ROSE}" fill-opacity="0.15" filter="url(#glow)"/>
      <rect x="380" y="128" width="98" height="20" rx="4" fill="{ROSE}"/>
      <text x="390" y="142" font-family="{MONO}" font-size="10.5" font-weight="700" fill="{BG}">NEAR MISS</text>
    </g>
    <text x="30" y="156" font-family="{MONO}" font-size="10" fill="{MUTED}">YOLO11 + ByteTrack · surrogate safety scoring</text>'''
    style = """
    .carA { animation: carA 6s cubic-bezier(.45,.05,.55,.95) infinite; }
    @keyframes carA { 0% { transform: translate(-60px,70px) } 55% { transform: translate(312px,70px) } 100% { transform: translate(640px,70px) } }
    .bike { animation: bike 6s cubic-bezier(.45,.05,.55,.95) infinite; }
    @keyframes bike { 0% { transform: translate(342px,-40px) } 50% { transform: translate(342px,34px) } 60% { transform: translate(342px,38px) } 100% { transform: translate(342px,190px) } }
    .alert { opacity: 0; animation: alert 6s ease-out infinite; }
    @keyframes alert { 0%,46% { opacity: 0 } 52% { opacity: 1 } 78% { opacity: 1 } 90%,100% { opacity: 0 } }
    """
    svg = card_frame(
        W, H, "Reflex", "Collision risk detection from traffic video",
        [("94.4% F1", "vehicle detection · Urban Tracker"), ("87.6%", "near miss precision"), ("3.8× faster", "TensorRT · 12 → 46 FPS")],
        "PyTorch · YOLO11 · OpenCV · TensorRT · FastAPI · React · PostgreSQL",
        scene, "COMPUTER VISION", style,
    )
    (OUT / "reflex.svg").write_text(svg)


def radarmd():
    W, H = 590, 376
    cx, cy = 200, 92
    ribs = []
    for k in range(6):
        y = 44 + k * 17
        spread = 70 + k * 6
        ribs.append(f'<path d="M{cx-6},{y} C{cx-spread*0.5},{y-10} {cx-spread},{y+2} {cx-spread-6},{y+18}"/>')
        ribs.append(f'<path d="M{cx+6},{y} C{cx+spread*0.5},{y-10} {cx+spread},{y+2} {cx+spread+6},{y+18}"/>')
    labels = ["Atelectasis", "Cardiomegaly", "Effusion", "Infiltration", "Mass", "Nodule", "Pneumonia"]
    lab = "".join(
        f'<text x="372" y="{44 + i*16}" font-family="{MONO}" font-size="10" fill="{MUTED}" class="lab" style="animation-delay:{i*0.35:.2f}s">{l}</text>'
        for i, l in enumerate(labels)
    )
    scene = f'''
    <rect x="16" y="16" width="{W-32}" height="150" fill="#05080f"/>
    <defs>
      <radialGradient id="cam" cx="0.5" cy="0.5" r="0.5">
        <stop offset="0" stop-color="#ef4444" stop-opacity="0.85"/><stop offset="0.45" stop-color="{AMBER}" stop-opacity="0.45"/>
        <stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>
      <radialGradient id="body" cx="0.5" cy="0.45" r="0.6"><stop offset="0" stop-color="#94a3b8" stop-opacity="0.22"/><stop offset="1" stop-color="#94a3b8" stop-opacity="0"/></radialGradient>
      <linearGradient id="scan" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0.5"/></linearGradient>
    </defs>
    <ellipse cx="{cx}" cy="{cy+6}" rx="130" ry="80" fill="url(#body)"/>
    <path d="M{cx-14},40 C{cx-80},34 {cx-104},90 {cx-96},150 L{cx-20},150 C{cx-14},110 {cx-12},70 {cx-14},40Z" fill="#cbd5e1" fill-opacity="0.07" stroke="#cbd5e1" stroke-opacity="0.35"/>
    <path d="M{cx+14},40 C{cx+80},34 {cx+104},90 {cx+96},150 L{cx+20},150 C{cx+14},110 {cx+12},70 {cx+14},40Z" fill="#cbd5e1" fill-opacity="0.07" stroke="#cbd5e1" stroke-opacity="0.35"/>
    <g fill="none" stroke="#e2e8f0" stroke-opacity="0.28" stroke-width="2.2" stroke-linecap="round">{''.join(ribs)}</g>
    <rect x="{cx-4}" y="24" width="8" height="140" rx="3" fill="#e2e8f0" fill-opacity="0.18"/>
    <ellipse cx="{cx+52}" cy="{cy+22}" rx="38" ry="30" fill="url(#cam)" class="cam"/>
    <rect x="{cx+20}" y="{cy-6}" width="66" height="54" fill="none" stroke="{ACCENT}" stroke-width="1.4" stroke-dasharray="5 4"/>
    <rect x="{cx+20}" y="{cy-20}" width="58" height="13" fill="{ACCENT}"/>
    <text x="{cx+25}" y="{cy-10}" font-family="{MONO}" font-size="9" font-weight="700" fill="#05080f">GT box</text>
    <rect x="16" y="16" width="{W-32}" height="26" fill="url(#scan)" class="scan"/>
    <line x1="352" y1="28" x2="352" y2="156" stroke="{BORDER}"/>
    {lab}
    <text x="372" y="{44 + 7*16}" font-family="{MONO}" font-size="10" fill="{ACCENT}">+ 7 more labels</text>
    <text x="30" y="156" font-family="{MONO}" font-size="10" fill="{MUTED}">Grad-CAM vs ground truth</text>'''
    style = """
    .cam { transform-box: fill-box; transform-origin: center; animation: cam 3.4s ease-in-out infinite; }
    @keyframes cam { 0%,100% { opacity: .55; transform: scale(.9) } 50% { opacity: 1; transform: scale(1.06) } }
    .scan { animation: scan 4.5s linear infinite; }
    @keyframes scan { 0% { transform: translateY(-30px) } 100% { transform: translateY(160px) } }
    .lab { animation: lab 4.9s ease-in-out infinite; }
    @keyframes lab { 0%,100% { fill: #94a3b8 } 12% { fill: #38bdf8 } 30% { fill: #94a3b8 } }
    """
    svg = card_frame(
        W, H, "RadarMD", "Multi label chest X-ray triage · 14 pathologies",
        [("0.84 AUROC", "mean · +6 pts over baseline"), ("<8%", "missed diagnoses"), ("4× faster", "ONNX CPU · ~120 ms/image")],
        "PyTorch Lightning · DenseNet-121 · ConvNeXt · MONAI · ONNX · Cloud Run",
        scene, "MEDICAL IMAGING", style,
    )
    (OUT / "radarmd.svg").write_text(svg)


def divider():
    W, H = 1200, 6
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" aria-hidden="true">
  <defs>
    <linearGradient id="base" x1="0" x2="1"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/><stop offset="0.5" stop-color="{BORDER}"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></linearGradient>
    <linearGradient id="spark" x1="0" x2="1"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/><stop offset="0.5" stop-color="{ACCENT}"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></linearGradient>
  </defs>
  <style>.s {{ animation: s 5s cubic-bezier(.45,.05,.55,.95) infinite; }} @keyframes s {{ from {{ transform: translateX(-240px) }} to {{ transform: translateX(1200px) }} }}
  @media (prefers-reduced-motion: reduce) {{ .s {{ animation: none; opacity: 0 }} }}</style>
  <rect y="2.5" width="{W}" height="1" fill="url(#base)"/>
  <rect class="s" y="2" width="240" height="2" rx="1" fill="url(#spark)"/>
</svg>'''
    (OUT / "divider.svg").write_text(svg)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    hero(); impact(); reflex(); radarmd(); divider()
    print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
