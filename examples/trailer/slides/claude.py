"""46.5-52.5 s: Claude fixes it. The note goes to the chat, the change comes in line by line, a
blue line renders the slide again with a red heart, and the slide is approved."""

import math

from manim import UL, VGroup

from kit import (AZUL, GRAFITO, NIEBLA, U, Clip, El, Slide, back, border, box, clamp, cursor, dot,
                 hue_rotate, inout, keyframes, lerp, line, out4, p, path, pill, put, recolor, rise, run, text)
from style import OK, palette

CODE = [(0, 380), (1, 300), (2, 420), (1, 260), (0, 340), (1, 400)]  # kind (0 same, 1 in, 2 out), width
SIGN = {0: ("", "#5b616b", "#e7e8eb"), 1: ("+", OK, "#cdebd8"), 2: ("−", "#c2410c", "#fbd5c4")}
CHECK = "M5 12.5 L9.5 17 L19 7.5"


class Fix:
    """The slide: the old heart, and the new one behind a blue line that sweeps from the left."""

    def __init__(self):
        heart = Slide("fourier-circles", "any_shape")
        light = palette("light")
        self.sweep = 0.0

        def look(rgb):
            old = recolor(rgb, heart.colors, light)
            cut = int(self.sweep * old.shape[1])
            if cut:
                old[:, :cut] = hue_rotate(old[:, :cut], 133, 1.3)
            return old

        self.film = Clip(heart, 1080, 608, 20, a=46.5, off=20, rate=0.5, look=look)
        self.edge = border(1080, 608)
        self.glow = El(box(50, 608, 0, AZUL).set_fill(opacity=0.18))
        self.scan = El(box(10, 608, 0, AZUL))
        self.mobjects = [self.film.el.m, self.edge.m, self.glow.m, self.scan.m]

    def frame(self, t):
        fe = out4(p(t, 46.5, 47.0))
        o = fe * (1 - p(t, 52.0, 52.4))
        s = lerp(0.96, 1, fe)
        self.sweep = sweep = inout(p(t, 49.2, 50.3))
        self.film.show(t, 660, 574, s=s, o=o)
        self.edge.at(660, 574, s=s, o=o)
        scanning = 1 if 49.2 < t < 50.35 else 0
        x = 120 + sweep * 1080
        self.glow.at(x, 574, o=o * scanning)
        self.scan.at(x, 574, o=o * scanning)


class Chat:
    def __init__(self):
        self.panel = El(box(540, 608, 20, "#ffffff", NIEBLA, 2), UL)
        words = [text(s, 34, 500, "#ffffff") for s in ("Make it red, and draw", "it slower")]
        w = max(x.width for x in words) / U + 56
        h = 34 * 1.276 * 2 + 40
        shape = box(w, h, 28, GRAFITO)
        corner = box(28, 28, 0, GRAFITO).move_to(shape.get_corner([1, -1, 0]) + [-14 * U, 14 * U, 0])
        corner2 = box(28, 28, 8, GRAFITO).move_to(corner)
        for i, x in enumerate(words):
            x.move_to(shape.get_corner(UL) + [28 * U + x.width / 2, -(20 + 34 * 0.984 + i * 34 * 1.276) * U - x.baseline, 0])
        self.bubble = El(VGroup(shape, corner, corner2, *words), [1, -1, 0])
        self.bubble_w, self.bubble_h = w, h
        self.rows = []
        for i, (k, width) in enumerate(CODE):
            sign, color, bar = SIGN[k]
            parts = [box(width, 20, 10, bar).move_to([(40 + width / 2) * U, 0, 0])]
            if sign:
                parts.append(text(sign, 30, 600, color).move_to([13 * U, 0, 0]))
            self.rows.append(El(VGroup(*parts), [-1, 0, 0]))
        self.dots = [El(dot(22, AZUL)) for _ in range(3)]
        self.mobjects = [self.panel.m, self.bubble.m] + [r.m for r in self.rows] + [d.m for d in self.dots]

    def frame(self, t):
        ce = out4(p(t, 46.6, 47.1))
        o = ce * (1 - p(t, 52.0, 52.4))
        dx = (1 - ce) * 200
        self.panel.at(1260 + dx, 270, o=o)
        ub = back(p(t, 46.9, 47.3))
        self.bubble.at(1260 + 540 - 30 + dx, 300 + self.bubble_h, s=max(ub, 0.001), o=o * clamp(ub))
        thinking = 47.3 < t < 48.2
        for i, d in enumerate(self.dots):
            jump = -14 * max(0, math.sin((t - 47.3) * 9 - i * 0.9))
            d.at(1260 + 30 + 11 + i * 34 + dx, 470 + 11 + jump, o=o if thinking else 0)
        for i, r in enumerate(self.rows):
            e = out4(p(t, 48.2 + i * 0.14, 48.5 + i * 0.14))
            r.at(1290 + (1 - e) * -30 + dx, 470 + 19 + i * 58, o=o * e)


class Approve:
    def __init__(self):
        def icon():
            return path(CHECK, stroke="#ffffff", width=2.6, scale=1.5)
        self.off, self.w, self.h = pill("Approve", 36, 500, "#ffffff", GRAFITO, None, 34, 16, width=0, icon=icon(), gap=14)
        self.on, _, _ = pill("Approved", 36, 500, "#ffffff", OK, None, 34, 16, width=0, icon=icon(), gap=14)
        self.burst = [El(dot(14, AZUL if i % 2 else OK)) for i in range(14)]
        self.mobjects = [self.off.m, self.on.m] + [b.m for b in self.burst]

    def frame(self, t):
        ap = back(p(t, 50.4, 50.8))
        o = clamp(ap) * (1 - p(t, 52.0, 52.4))
        pressed = t > 51.2
        for el, show in ((self.off, not pressed), (self.on, pressed)):
            el.at(1260, 920, s=max(ap, 0.001), o=o if show else 0)
        e = out4(p(t, 51.2, 51.9))
        for i, b in enumerate(self.burst):
            ang = i / 14 * math.pi * 2
            b.at(1407 + math.cos(ang) * 170 * e, 957 + math.sin(ang) * 110 * e,
                 o=(1 - p(t, 51.6, 52.0)) if t > 51.2 else 0)


def build(scene):
    title = put(text("Claude fixes it", 96, spacing=-0.04), 120, line(96, 110))
    fix, chat, approve = Fix(), Chat(), Approve()
    arrow = cursor()
    keys = [(50.4, 1700, 1100), (51.1, 1340, 945), (51.6, 1340, 945)]

    def frame(t):
        rise(title, t, 46.6, 120, line(96, 110), 96, 52.0)
        fix.frame(t)
        chat.frame(t)
        approve.frame(t)
        x, y = keyframes(t, keys)
        arrow.at(x, y, s=0.85 if 51.2 < t < 51.38 else 1, o=p(t, 50.4, 50.6) * (1 - p(t, 51.8, 52.0)))

    run(scene, 46.5, 52.5, frame, title.m, *fix.mobjects, *chat.mobjects, *approve.mobjects, arrow.m)
