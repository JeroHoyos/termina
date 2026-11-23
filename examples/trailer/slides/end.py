"""68.5-76 s: the end. The name, what Termina is, where to get it, and that this trailer is made
with Termina; then the screen fades."""

from manim import VGroup

from kit import ACERO, NIEBLA, U, El, back, box, clamp, lerp, line, out4, p, pill, put, rise, run, text
from .logo import K, LETTERS, letters
from style import AZUL, GRAFITO, HUESO

# The wordmark of docs/images/wordmark.svg: its viewBox starts at (30, 30) and is 1730 wide; it
# is 840 pixels wide at (540, 330).
SCALE = 840 / 1730


def wordmark():
    """The logo of logo.py, whole, anchored at the top left of the viewBox of the wordmark."""
    k = SCALE / K
    parts = [box(400 * SCALE, 100 * SCALE, 50 * SCALE, GRAFITO).move_to([256, -90, 0]),
             box(100 * SCALE, 295 * SCALE, 50 * SCALE, GRAFITO).move_to([256, -187.5, 0]),
             box(112 * SCALE, 112 * SCALE, 56 * SCALE, AZUL).move_to([256, -422, 0]),
             box(60 * SCALE, 60 * SCALE, 30 * SCALE, AZUL).move_to([1238, -84, 0])]
    for m in parts:  # the centers above are in units of the SVG
        m.move_to(m.get_center() * SCALE * U)
    strokes = [m.scale(k, about_point=[0, 0, 0]).shift([-16 * SCALE * U, 0, 0]) for m in letters()]
    for s in strokes:
        s.set_stroke(width=s.get_stroke_width() * k)
    assert len(strokes) == len(LETTERS)
    return El(VGroup(*parts, *strokes), origin=[30 * SCALE * U, -30 * SCALE * U, 0])


def build(scene):
    mark = wordmark()
    tagline = put(text("Talks made with math, one slide at a time", 48, 400, ACERO, -0.015), 960,
                  line(48, 640, 1.276), "center")
    link = put(text("github.com/JeroHoyos/termina", 32, 500, GRAFITO, 0.06, mono=True), 960,
               line(32, 770, 1.276), "center")
    small = put(text("OPEN SOURCE   MIT   WINDOWS AND LINUX", 26, 500, ACERO, 0.14, mono=True), 960,
                line(26, 840, 1.276), "center")
    made, made_w, made_h = pill("This trailer was made with Termina", 30, 500, GRAFITO, "#ffffff", NIEBLA, 26, 12,
                                icon=box(18, 18, 9, AZUL), gap=14)
    curtain = El(box(1920, 1080, 0, HUESO))

    def frame(t):
        e = out4(p(t, 68.5, 69.2))
        mark.at(540 + 420 * (1 - lerp(0.9, 1, e)), 330 + 111 * (1 - lerp(0.9, 1, e)), s=lerp(0.9, 1, e), o=e)
        rise(tagline, t, 69.2, 960, line(48, 640, 1.276), 48, d=0.8)
        link.at(960, line(32, 770, 1.276), o=p(t, 69.9, 70.5))
        small.at(960, line(26, 840, 1.276), o=p(t, 70.3, 70.9))
        e = back(p(t, 71.2, 71.6))
        made.at(960 - made_w / 2 * e, 915 + made_h / 2 * (1 - e), s=max(e, 0.001), o=clamp(e))
        curtain.at(960, 540, o=p(t, 74.6, 75.8))

    run(scene, 68.5, 76, frame, mark.m, tagline.m, link.m, small.m, made.m, curtain.m)
