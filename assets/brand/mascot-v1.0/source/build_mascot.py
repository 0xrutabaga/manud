"""Build the Little Manud SVG production candidates (A3 Pebble v2 direction).

Geometry is traced by hand from previews/round2/manud-A3-pebble-v02-original.png
(1024 px canvas) and then refined; all coordinates below are in that 1024 space and
scaled to each SVG's viewBox at write time. Stdlib only.

Usage: python build_mascot.py <out_dir>
"""
import math
import sys
from pathlib import Path

CORAL, INK, CREAM = "#FF95A5", "#1E2A4A", "#FFF6DC"

# --- Body centre line (stroke centre), traced from A3 v2 -------------------------
# Polar samples of the outer edge from the body centre (520, 534), inset by half the
# 21 px stroke. Angles are maths angles (counter-clockwise, y up).
CENTRE = (520.0, 534.0)
OUTER_R = {0: 338, 15: 340, 30: 341, 45: 337, 60: 325, 75: 307, 90: 293, 105: 289,
           120: 295, 135: 306, 150: 317, 165: 326, 180: 330, 195: 328, 210: 322,
           255: 291, 270: 285, 285: 287, 300: 296, 315: 309, 330: 322, 345: 332}
HALF = 10.5


def polar(deg):
    t = math.radians(deg)
    r = OUTER_R[deg] - HALF
    return (CENTRE[0] + r * math.cos(t), CENTRE[1] - r * math.sin(t))


# Clockwise on screen, starting on the right side just below the loop.
S, E = polar(60), polar(30)          # where the outline hands over to / back from the loop
RIGHT_BOTTOM = [polar(d) for d in (15, 0, 345, 330, 315, 300, 285, 270, 255)]
# Tail, traced from the gridded crop and smoothed into one soft notch (the original has a
# hard corner where the tail rejoins the bottom edge).
TAIL = [(372, 794), (318, 781), (244, 795), (211, 772), (222, 738), (250, 703)]
TOP_LEFT = [polar(d) for d in (195, 180, 165, 150, 135, 120, 105, 90, 75)]
# Refined signature loop. The outline is one pen line: it rises off the top-right shoulder,
# turns one closed cursive loop counter-clockwise (the way a Thai letter starts at its round
# head and the line crosses itself), passes back through the crossing point X and settles
# onto the shoulder again. No stem, no free end.
X = (742, 284)                        # crossing point, just above the original shoulder
RISE = [(712, 272)]
LOOP = [(782, 264), (806, 226), (794, 186), (756, 170), (720, 186), (710, 226)]
FALL = [(774, 322)]
LOOP_TILT_DEG = 50                    # lean the loop outward so it reads as a flourish, not a hanging tag


def _rotate(pts, about, deg):
    t = math.radians(deg)
    c, sn = math.cos(t), math.sin(t)
    return [(about[0] + (x - about[0]) * c - (y - about[1]) * sn,
             about[1] + (x - about[0]) * sn + (y - about[1]) * c) for x, y in pts]


LOOP = _rotate(LOOP, X, LOOP_TILT_DEG)

LINE_PTS = RIGHT_BOTTOM + TAIL + TOP_LEFT + [S] + RISE + [X] + LOOP + [X] + FALL + [E]
FILL_PTS = RIGHT_BOTTOM + TAIL + TOP_LEFT + [S] + RISE + [X] + FALL + [E]


def catmull_rom(points, closed=True):
    """Return an SVG path 'd' through points using uniform Catmull-Rom -> cubic Bezier."""
    p = points
    n = len(p)
    out = [f"M{p[0][0]:.1f} {p[0][1]:.1f}"]
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = p[(i - 1) % n] if closed or i > 0 else p[i]
        p1, p2 = p[i], p[(i + 1) % n]
        p3 = p[(i + 2) % n] if closed or i + 2 < n else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        out.append(f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}")
    if closed:
        out.append("Z")
    return " ".join(out)


def transform_pts(pts, s, dx, dy):
    return [(x * s + dx, y * s + dy) for x, y in pts]


def bbox(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


EYES = [(408, 517), (635, 517)]
EYE_RX, EYE_RY = 19, 35
MOUTH = [(474, 602), (522, 603), (556, 598), (582, 579)]


def fit(view, margin, extra_pad):
    """Scale + offset so the outline (incl. stroke) is centred in a square viewBox."""
    x0, y0, x1, y1 = bbox(LINE_PTS)
    x0 -= extra_pad; y0 -= extra_pad; x1 += extra_pad; y1 += extra_pad
    s = (view - 2 * margin) / max(x1 - x0, y1 - y0)
    dx = (view - (x1 - x0) * s) / 2 - x0 * s
    dy = (view - (y1 - y0) * s) / 2 - y0 * s
    return s, dx, dy


def svg(view, title, *, stroke, mouth=True, eye_scale=1.0, mouth_w=None, rim=None,
        loop_scale=1.0, margin=None, line_color=INK):
    margin = view * 0.06 if margin is None else margin
    pad = stroke / 2 + (rim or 0) / 2   # stroke + rim extend beyond the centre line
    s, dx, dy = fit(view, margin, pad)
    loop = LOOP
    if loop_scale != 1.0:  # enlarge the loop about the crossing so its hole survives tiny sizes
        loop = [(X[0] + (x - X[0]) * loop_scale, X[1] + (y - X[1]) * loop_scale) for x, y in LOOP]
    line_pts = RIGHT_BOTTOM + TAIL + TOP_LEFT + [S] + RISE + [X] + loop + [X] + FALL + [E]
    fill_d = catmull_rom(transform_pts(FILL_PTS, s, dx, dy))
    line_d = catmull_rom(transform_pts(line_pts, s, dx, dy))
    sw = stroke * s
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view} {view}" '
             f'width="{view}" height="{view}" role="img" aria-labelledby="t">',
             f'<title id="t">{title}</title>']
    if rim:
        parts.append(f'<path d="{line_d}" fill="none" stroke="{CREAM}" stroke-width="{(stroke + rim) * s:.2f}" '
                     'stroke-linejoin="round" stroke-linecap="round"/>')
    parts.append(f'<path d="{fill_d}" fill="{CORAL}"/>')
    parts.append(f'<path d="{line_d}" fill="none" stroke="{line_color}" stroke-width="{sw:.2f}" '
                 'stroke-linejoin="round" stroke-linecap="round"/>')
    for ex, ey in EYES:
        cx, cy = ex * s + dx, ey * s + dy
        parts.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{EYE_RX * eye_scale * s:.2f}" '
                     f'ry="{EYE_RY * eye_scale * s:.2f}" fill="{INK}"/>')
    if mouth:
        m = transform_pts(MOUTH, s, dx, dy)
        d = (f"M{m[0][0]:.1f} {m[0][1]:.1f} L{m[1][0]:.1f} {m[1][1]:.1f} "
             f"Q{m[2][0]:.1f} {m[2][1] + 4 * s:.1f} {m[3][0]:.1f} {m[3][1]:.1f}")
        parts.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{(mouth_w or 19) * s:.2f}" '
                     'stroke-linecap="round" stroke-linejoin="round"/>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    name = "Little Manud, the MANUD mascot: a coral speech bubble with a Thai-letter loop"
    files = {
        # Standard (>= 48 px): faithful A3 v2 proportions.
        "manud-mascot-light.svg": svg(512, name, stroke=22),
        # Dark backgrounds: same character plus a cream outer rim so the ink outline and loop stay visible.
        "manud-mascot-dark.svg": svg(512, name, stroke=22, rim=26),
        # Simplified 32 px icon: heavier outline, larger eyes, shorter mouth, larger loop.
        # Small dark icons use a cream outline instead of a rim (a rim turns to grey mush at 16-32 px).
        "manud-icon-32-light.svg": svg(32, name, stroke=48, eye_scale=1.35, mouth_w=34,
                                       loop_scale=1.1, margin=1),
        "manud-icon-32-dark.svg": svg(32, name, stroke=48, eye_scale=1.35, mouth_w=34,
                                      loop_scale=1.1, margin=1, line_color=CREAM),
        # Simplified 16 px icon: no mouth, heaviest outline; the loop reads as a bump.
        "manud-icon-16-light.svg": svg(16, name, stroke=72, eye_scale=1.7, mouth=False,
                                       loop_scale=1.2, margin=0.5),
        "manud-icon-16-dark.svg": svg(16, name, stroke=72, eye_scale=1.7, mouth=False,
                                      loop_scale=1.2, margin=0.5, line_color=CREAM),
    }
    for fn, text in files.items():
        (out / fn).write_text(text, encoding="utf-8")
        print(fn, len(text), "bytes")


if __name__ == "__main__":
    main(sys.argv[1])
