"""10.5-22.5 s: four ways to use Termina. Each device comes from the right and leaves to the
left: a class, a research talk, a reel and a video."""

import math

from manim import ORIGIN, UL, CapStyleType, Line, VGroup

from kit import (ACERO, AZUL, GRAFITO, NIEBLA, P, U, Clip, El, Slide, View, sw, back, border, box, clamp, dot,
                 inout, line, out4, p, path, put, recolor, rise, run, text)
from style import palette

USES = [("Teach", "a class with moving math"), ("Present", "your research"), ("Post", "a reel"),
        ("Publish", "a video")]
HEART = "M0 -10 C -18 -38 -56 -24 -50 4 C -44 30 -14 44 0 60 C 14 44 44 30 50 4 C 56 -24 18 -38 0 -10Z"
FRAME = (780 + 520, 190 + 292.5)  # the center of the 1040 x 585 frame of a slide


class Words:
    """The number, the word and the line on the left, and the four dots of progress."""

    def __init__(self):
        self.nums = [put(text(f"0{i + 1}", 26, 500, AZUL, 0.14, mono=True), 120, line(26, 300, 1.276)) for i in range(4)]
        self.words = [put(text(w, 140, spacing=-0.045), 126, line(140, 350)) for w, _ in USES]
        self.subs = [put(text(s, 48, 400, ACERO, -0.015), 122, line(48, 520, 1.276)) for _, s in USES]
        self.dots = [El(box(64, 10, 5, AZUL), UL) for _ in USES]
        self.mobjects = [e.m for g in (self.nums, self.words, self.subs, self.dots) for e in g]

    def frame(self, t):
        k = min(3, math.floor((t - 10.5) / 3))
        a = 10.5 + k * 3
        for i in range(4):
            on = i == k
            self.nums[i].at(120, line(26, 300, 1.276), o=(p(t, a, a + 0.3) * (1 - p(t, a + 2.75, a + 2.95))) if on else 0)
            if on:
                rise(self.words[i], t, a + 0.05, 126, line(140, 350), 140, a + 2.75 if k < 3 else 22.1)
                rise(self.subs[i], t, a + 0.2, 122, line(48, 520, 1.276), 48, a + 2.8 if k < 3 else 22.15)
            else:
                self.words[i].at(0, 0, o=0)
                self.subs[i].at(0, 0, o=0)
        self.progress(t, k)

    def progress(self, t, k):
        x, o = 120, p(t, 10.6, 11) * (1 - p(t, 22.1, 22.4))
        for i, d in enumerate(self.dots):
            w = 64 if i == k else 20
            d.base.set_fill(AZUL if i == k else GRAFITO if i < k else NIEBLA)
            d.at(x, 760, sx=w / 64, o=o)
            x += w + 16


def view(t, i):
    """Where device i is: it slides in from the right, and out to the left."""
    s = 10.5 + i * 3
    if not s - 0.1 <= t < s + 3.1:
        return None
    come, go = out4(p(t, s, s + 0.6)), inout(p(t, s + 2.7, s + 3.0))
    last = inout(p(t, 22.0, 22.5)) if i == 3 else 0
    return View(dx=(1 - come) * 900 - go * 1300, s=1 - last * 0.1, cx=1340, cy=540, o=1 - last)


def person(color, head=64):
    """Someone in the audience, seen from behind: a head and round shoulders. Anchored at the top
    of the head."""
    top = dot(head, color)
    shoulders = box(head * 1.9, head * 3, head * 0.9, color)  # it goes on under the bottom edge
    shoulders.next_to(top, direction=[0, -1, 0], buff=8 * U)
    return El(VGroup(top, shoulders), [0, 1, 0])


# The audience: a back row (smaller, gray) and a front row between its gaps. x, top of the head, scale
SEATS = [(815 + i * 150, 812, 0.8, ACERO) for i in range(7)] + [(890 + i * 150, 860, 1.0, GRAFITO) for i in range(6)]


class Class:
    def __init__(self):
        # From 15 s the slide shows b² and a² going into a² + b² = c², whole before the device leaves.
        self.film = Clip(Slide("manimgx-examples", "pythagoras"), 1040, 585, 20, a=10.5, off=15.0, rate=1.3)
        self.line = border(1040, 585)
        self.people = [person(color) for *_, color in SEATS]
        self.mobjects = [self.film.el.m, self.line.m] + [h.m for h in self.people]

    def frame(self, t, v):
        if v is None:
            return hide(self)
        v.show(self.film, t, *FRAME)
        v.at(self.line, *FRAME)
        order = sorted(range(len(SEATS)), key=lambda i: SEATS[i][0])
        for n, i in enumerate(order):
            x, y, s, _ = SEATS[i]
            e = back(p(t, 10.9 + n * 0.05, 11.3 + n * 0.05))
            v.at(self.people[i], x, y + (1 - clamp(e)) * 280 + (e - 1) * -20, s=s)


# The speaker, in pixels from the top left of its 220 px box: an arm that bends at the elbow, and
# a hand whose finger points (the laser starts at its tip).
SHOULDER, ELBOW, PALM, HAND = (180, 214), (258, 250), (320, 182), (350, 166)


def limb(a, b, width):
    """A part of the arm from a to b, with round ends."""
    part = Line([a[0] * U, -a[1] * U, 0], [b[0] * U, -b[1] * U, 0])
    return part.set_stroke(GRAFITO, sw(width)).set_cap_style(CapStyleType.ROUND)


class Research:
    def __init__(self):
        self.film = Clip(Slide("manimgx-examples", "hopf_fibration"), 1040, 585, 20, a=13.5, off=13)
        self.line = border(1040, 585)
        self.laser = El(VGroup(dot(70, AZUL).set_fill(opacity=0.12), dot(46, AZUL).set_fill(opacity=0.25), dot(26, AZUL)))
        self.beam = Line(P(0, 0), P(1, 1)).set_stroke(AZUL, sw(4), opacity=0)
        arm = VGroup(limb(SHOULDER, ELBOW, 50), limb(ELBOW, PALM, 40), limb(PALM, HAND, 14))
        joints = VGroup(*(dot(d, GRAFITO).move_to([x * U, -y * U, 0]) for d, (x, y) in ((60, SHOULDER), (44, ELBOW), (46, PALM))))
        body = VGroup(dot(140, GRAFITO).move_to([110 * U, -80 * U, 0]),
                      box(200, 350, 100, GRAFITO).move_to([110 * U, -345 * U, 0]), arm, joints)
        self.speaker = El(body, origin=ORIGIN)
        self.mobjects = [self.film.el.m, self.line.m, self.beam, self.laser.m, self.speaker.m]

    def frame(self, t, v):
        if v is None:
            return hide(self)
        v.show(self.film, t, *FRAME)
        v.at(self.line, *FRAME)
        u = (t - 13.5) * 2.2
        dot_at = (780 + 520 + 170 * math.cos(u), 190 + 280 + 110 * math.sin(u * 1.3))
        shine = p(t, 14.0, 14.3)
        v.at(self.laser, *dot_at, o=shine)
        y = 560 + (1 - out4(p(t, 13.7, 14.2))) * 520
        v.at(self.speaker, 610, y)
        hand = v.xy(610 + HAND[0], y + HAND[1])
        self.beam.put_start_and_end_on(P(*hand), P(*v.xy(*dot_at)))
        self.beam.set_stroke(opacity=0.35 * shine * v.o)


class Reel:
    def __init__(self):
        self.phone = El(box(400, 860, 56, GRAFITO))
        self.film = Clip(Slide("manimgx-examples", "catenoid_helicoid"), 368, 828, 42, a=16.5, off=12, zoom=1.35)
        self.hearts = [El(path(HEART, AZUL if i % 3 else GRAFITO)) for i in range(12)]
        self.mobjects = [self.phone.m, self.film.el.m] + [h.m for h in self.hearts]

    def frame(self, t, v):
        if v is None:
            return hide(self)
        v.at(self.phone, 1110 + 200, 110 + 430)
        v.show(self.film, t, 1110 + 200, 110 + 430)
        for i, h in enumerate(self.hearts):
            at = 17.2 + i * 0.12
            e = p(t, at, at + 1.4)
            x = 700 + (i % 4) * 70 + 50 * math.sin(i * 2.1 + e * 4)
            s = 170 * (0.6 + 0.4 * ((i * 7) % 3) / 2)
            k = s / 130
            v.at(h, 760 + x + s / 2, 820 - e * 640 + 71 * k, s=k * back(p(t, at, at + 0.3)),
                 o=math.sin(e * math.pi) if e > 0 else 0, r=(1 if i % 2 else -1) * 14 * e)


class Video:
    def __init__(self):
        look = palette("light")
        self.film = Clip(Slide("strange-attractor", "the_attractor"), 1040, 585, 20, a=19.5, off=9, rate=1.2)
        self.film.look = lambda rgb: recolor(rgb, self.film.slide.colors, look)
        self.line = border(1040, 585)
        self.bar = El(box(1040, 84, 20, "#ffffff", NIEBLA, 2), UL)
        self.track = El(box(984, 8, 4, NIEBLA), UL)
        self.done = El(box(984, 8, 4, AZUL), UL)
        self.play = El(VGroup(dot(160, GRAFITO), path("M-16 -32 L36 0 L-16 32Z", "#ffffff")))
        self.mobjects = [self.bar.m, self.film.el.m, self.line.m, self.play.m, self.track.m, self.done.m]

    def frame(self, t, v):
        if v is None:
            return hide(self)
        v.at(self.bar, 780, 805 - 20)
        v.show(self.film, t, 780 + 520, 220 + 292.5)
        v.at(self.line, 780 + 520, 220 + 292.5)
        pb = p(t, 20.0, 20.3)
        v.at(self.play, 780 + 520, 220 + 292, s=1 + pb * 0.6, o=1 - pb)
        v.at(self.track, 808, 833)
        done = p(t, 20.1, 22.2)
        v.at(self.done, 808, 833, sx=max(done, 0.001), o=1 if done > 0 else 0)


def hide(device):
    for m in device.mobjects:
        m.set_opacity(0)


def build(scene):
    words = Words()
    devices = [Class(), Research(), Reel(), Video()]

    def frame(t):
        words.frame(t)
        for i, d in enumerate(devices):
            d.frame(t, view(t, i))

    run(scene, 10.5, 22.5, frame, *words.mobjects, *[m for d in devices for m in d.mobjects])
