"""32.5-46.5 s: six ways to guide a slide. A cursor points at the heart, circles it, moves its
label, writes a note, adds a picture and types a new title on the slide itself."""

import math

from manim import UL, DashedVMobject, VGroup, VMobject

from kit import (AZUL, GRAFITO, NIEBLA, U, Clip, El, P, Slide, back, blink, border, box, clamp,
                 cursor, dot, inout, keyframes, lerp, line, out4, p, path, picture, pill, put,
                 recolor, ring, ripple, rise, run, sw, text, typed)
from style import HUESO, palette

STEPS = [("Point at it", 32.5), ("Circle it", 34.5), ("Move it", 36.5), ("Write a note", 38.5),
         ("Add a picture", 40.5), ("Edit it yourself", 42.5)]
NOTE = "Make it red"
MORE = ", and draw it slower"
TITLE = "Forty circles, one heart"


def SX(x):
    """A point of the slide (1920 x 1080) on the stage, where the slide is 1280 x 720 at (320, 150)."""
    return x * 2 / 3 + 320


def SY(y):
    return y * 2 / 3 + 150


def loop(u):
    return 960 + 400 * math.cos(u), 640 + 360 * math.sin(u)


def light(slide):
    target = palette("light")
    return lambda rgb: recolor(rgb, slide.colors, target)


class Steps:
    def __init__(self):
        self.words = [put(text(w, 84, spacing=-0.04), 320, line(84, 30)) for w, _ in STEPS]
        self.dots = [(El(dot(20, None, AZUL, 3)), El(dot(20, AZUL))) for _ in STEPS]
        self.mobjects = [w.m for w in self.words] + [d.m for pair in self.dots for d in pair]

    def frame(self, t):
        k = max([i for i, (_, a) in enumerate(STEPS) if t >= a] or [0])
        a = STEPS[k][1]
        for i, w in enumerate(self.words):
            if i == k:
                rise(w, t, a + 0.02, 320, line(84, 30), 84, a + 1.75 if k < 5 else 45.9, 0.45)
            else:
                w.at(0, 0, o=0)
        self.progress(t, k, a)

    def progress(self, t, k, a):
        o = p(t, 32.6, 33) * (1 - p(t, 45.9, 46.3))
        for i, (empty, full) in enumerate(self.dots):
            s = 1 + 0.3 * (1 - out4(p(t, a, a + 0.4))) if i == k else 1
            x = 1600 - 190 + i * 34 + 10
            empty.at(x, 72, s=s, o=o)
            full.at(x, 72, s=s, o=o if i <= k else 0)


class Marks:
    """What the cursor leaves on the slide: a pin, an ink loop, a moved label, boxes, a title."""

    def __init__(self):
        self.pin = El(VGroup(dot(80, AZUL), text("1", 46, 600, "#ffffff").move_to([0, 0, 0])))
        bubble = VGroup(box(420, 92, 46, GRAFITO), text(NOTE, 50, 500, "#ffffff"))
        bubble[1].move_to(bubble[0]).align_to(bubble[0], [-1, 0, 0]).shift([40 * U, 0, 0])
        self.bubble = El(bubble, [-1, 0, 0])
        self.ink = VMobject().set_stroke(AZUL, sw(12 * 2 / 3))
        self.dest = El(DashedVMobject(box(290, 80, 12, None, AZUL, 5 * 2 / 3), num_dashes=24))
        curve = path("M1690 900 C 1760 700 1760 380 1695 195", stroke=AZUL, width=8 * 2 / 3, scale=2 / 3)
        self.trail = El(DashedVMobject(curve, num_dashes=40, dashed_ratio=0.15), origin=[0, 0, 0])
        self.cover = El(box(290 * 2 / 3, 80 * 2 / 3, 0, HUESO), UL)
        self.count = put(text("40 circles", 62 * 2 / 3, 700, AZUL, font="Segoe UI"), 0, 0)
        self.boxes = [El(box(w * 2 / 3, h * 2 / 3, 10 * 2 / 3, None, AZUL, 5 * 2 / 3), UL)
                      for w, h in ((1080, 100), (720, 640), (290, 80))]
        self.tcover = El(box(1080 * 2 / 3, 100 * 2 / 3, 0, HUESO), UL)
        self.title = [put(text(TITLE[:n], 76 * 2 / 3, 700, GRAFITO, font="Segoe UI"), 0, 0) if n else None
                      for n in range(len(TITLE) + 1)]
        self.caret = El(box(6 * 2 / 3, 76 * 2 / 3, 0, AZUL), UL)
        self.mobjects = [self.tcover.m] + [x.m for x in self.title if x] + [
            self.cover.m, self.count.m, self.ink, self.dest.m, self.trail.m, self.pin.m, self.bubble.m,
            *[b.m for b in self.boxes], self.caret.m]

    def frame(self, t, o):
        marks = o * (1 - p(t, 42.5, 42.8))
        self.point(t, marks)
        self.circle(t, marks)
        self.move(t, o)
        self.edit(t, o)

    def point(self, t, o):
        s = clamp(back(p(t, 33.5, 33.8)), 0, 1.3)
        self.pin.at(SX(800), SY(360), s=s * 2 / 3, o=o if t > 33.5 else 0)
        self.bubble.at(SX(800 + 60 * s), SY(360), s=s * 2 / 3, o=o * p(t, 33.8, 34.1))

    def circle(self, t, o):
        e = inout(p(t, 35.0, 36.1))
        n = int(60 * e)
        if t <= 35.0 or n < 1:
            self.ink.set_points_as_corners([P(0, 0), P(0, 0)]).set_stroke(opacity=0)
            return
        pts = [P(SX(loop(-2.2 + i / 60 * 6.6)[0]), SY(loop(-2.2 + i / 60 * 6.6)[1])) for i in range(n + 1)]
        self.ink.set_points_smoothly(pts).set_stroke(AZUL, sw(12 * 2 / 3), opacity=o)

    def move(self, t, o):
        hint = p(t, 36.6, 36.9) * (1 - p(t, 38.0, 38.2)) * o
        self.dest.at(SX(1550 + 145), SY(100 + 40), o=hint)
        self.trail.at(320, 150, o=hint)
        mv = inout(p(t, 37.1, 38.0))
        moved = o if t > 37.1 else 0
        self.cover.at(SX(1550), SY(915), o=moved)
        y = lerp(914, 100, mv)
        self.count.at(SX(1562), SY(y + 62 * 0.984), s=1 + 0.12 * math.sin(mv * math.pi), o=moved)

    def edit(self, t, o):
        boxes = p(t, 42.6, 42.9) * (1 - p(t, 45.0, 45.3)) * o
        for b, (x, y) in zip(self.boxes, ((80, 80), (600, 320), (1550, 100 if t > 38 else 915))):
            b.at(SX(x), SY(y), o=boxes)
        retype = t > 43.4
        self.tcover.at(SX(80), SY(80), o=o if retype else 0)
        shown = typed(TITLE, t, 43.6, 44.6) if retype else ""
        for n, el in enumerate(self.title):
            if el:
                el.at(SX(90), SY(84 + 76 * 0.984), o=o if n == len(shown) else 0)
        width = self.title[len(shown)].m.width / U if shown else 0
        self.caret.at(SX(96) + width, SY(96), o=o * blink(t) if 43.4 < t < 44.9 else 0)


class Note:
    """The bar under the slide: a note typed, and a picture that flies into it."""

    def __init__(self, still):
        self.bar = El(box(1280, 130, 20, "#ffffff", NIEBLA, 2), UL)
        self.num = El(VGroup(dot(56, AZUL), text("1", 32, 600, "#ffffff")))
        self.texts = [put(text(NOTE + MORE[:n], 46, 500), 0, 0) for n in range(len(MORE) + 1)]
        self.caret = El(box(4, 52, 0, AZUL), UL)
        self.send, w, h = pill("Send to Claude", 32, 500, "#ffffff", AZUL, None, 30, 16, width=0)
        self.sent, _, _ = pill("Send to Claude", 32, 500, "#ffffff", GRAFITO, None, 30, 16, width=0)
        self.send_h = h
        self.send_x = 320 + 1280 - 30 - w
        self.img_x = self.send_x - 20 - 160
        self.img = El(picture(still, 160, 90, 10))
        self.img_line = border(160, 90, 10)
        self.fly = El(picture(still, 560, 315, 16))
        self.fly_line = border(560, 315, 16)
        self.mobjects = [self.bar.m, self.num.m] + [x.m for x in self.texts] + [
            self.caret.m, self.img.m, self.img_line.m, self.send.m, self.sent.m, self.fly.m, self.fly_line.m]

    def frame(self, t):
        ne = out4(p(t, 38.9, 39.4))
        o = ne * (1 - p(t, 45.9, 46.3))
        dy = (1 - ne) * 60
        self.bar.at(320, 900 + dy, o=o)
        self.num.at(320 + 30 + 28, 965 + dy, o=o)
        shown = len(typed(MORE, t, 39.4, 40.5))
        for n, el in enumerate(self.texts):
            el.at(320 + 30 + 56 + 20, 965 + dy + 46 * 0.35, o=o if n == shown else 0)
        cx = 320 + 30 + 56 + 20 + self.texts[shown].m.width / U + 20
        self.caret.at(cx, 939 + dy, o=o * blink(t) if t < 41 else 0)
        pressed = 45.35 < t < 45.6
        self.send.at(self.send_x, 965 + dy - self.send_h / 2, o=0 if pressed else o)
        self.sent.at(self.send_x, 965 + dy - self.send_h / 2, o=o if pressed else 0)
        self.picture(t, o, dy)

    def picture(self, t, o, dy):
        fa = inout(p(t, 41.0, 41.8))
        landed = t >= 41.8
        s = back(p(t, 41.8, 42.1)) if landed else 1
        for el in (self.img, self.img_line):
            el.at(self.img_x + 80, 965 + dy, s=s, o=o if landed else 0)
        x, y = lerp(1960, self.img_x, fa), lerp(260, 920 + dy, fa)
        k = lerp(560, 160, fa) / 560
        flying = 1 if 40.9 < t < 41.8 else 0
        for el in (self.fly, self.fly_line):
            el.at(x + 280 * k, y + 157.5 * k, s=k, r=lerp(10, 0, fa), o=flying)


def keys():
    path_keys = [(32.5, 1700, 1100), (33.4, SX(800) - 4, SY(360) - 4), (34.6, SX(800), SY(360)),
                 (35.0, SX(loop(-2.2)[0]), SY(loop(-2.2)[1]))]
    for i in range(12):
        x, y = loop(-2.2 + (i + 1) / 12 * 6.6)
        path_keys.append((35.0 + (i + 1) / 12 * 1.1, SX(x), SY(y)))
    return path_keys + [(36.9, SX(1690), SY(945)), (37.1, SX(1690), SY(945)), (38.0, SX(1690), SY(130)),
                        (38.6, SX(1690), SY(130)), (39.2, 900, 960), (42.6, 900, 960), (43.3, SX(1140), SY(130)),
                        (44.8, SX(1140), SY(130)), (45.3, 1530, 925), (45.9, 1530, 925)]


def build(scene):
    heart = Slide("fourier-circles", "any_shape")
    attractor = Slide("strange-attractor", "the_attractor")
    film = Clip(heart, 1920, 1080, 30, a=32.5, off=15.3, rate=0.62, look=light(heart))
    edge = border(1280, 720)
    steps, marks = Steps(), Marks()
    note = Note(light(attractor)(attractor.still()))
    arrow, rip = cursor(), ring()
    path_keys = keys()
    clicks = [33.5, 37.1, 43.4, 45.35]

    def frame(t):
        steps.frame(t)
        fe = out4(p(t, 32.4, 32.9))
        o = fe * (1 - p(t, 45.9, 46.3))
        s = lerp(1.06, 1, fe)
        film.show(t, 960, 510, s=s * 2 / 3, o=o)
        edge.at(960, 510, s=s, o=o)
        marks.frame(t, o)
        note.frame(t)
        x, y = keyframes(t, path_keys)
        down = any(c < t < c + 0.18 for c in clicks)
        arrow.at(x, y, s=0.85 if down else 1, o=p(t, 32.8, 33.0) * (1 - p(t, 45.8, 46.0)))
        last = max([c for c in clicks if t > c - 0.5] or [33.5])
        ripple(rip, t, last, x + 8, y + 6)

    run(scene, 32.5, 46.5, frame, film.el.m, edge.m, *marks.mobjects, *note.mobjects,
        *steps.mobjects, arrow.m, rip.m)
