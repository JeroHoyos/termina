"""22.5-28.5 s: change one slide, render only that one. Four cards; the third one changes,
renders, and is up to date again, while the others wait."""

from manim import UL

from kit import AZUL, El, NIEBLA, Slide, box, dot, line, out4, p, picture, put, rise, run, text
from style import HIELO, OK

THUMBS = ["clifford_torus", "turing_torus", "hopf_fibration", "kaleidoscope_sphere"]
STATES = [("up to date", OK), ("changed", "#b45309"), ("rendering", AZUL), ("up to date", OK)]
CARD_H = 14 + 186 + 16 + 36 + 14 + 8 + 18


def state_at(t):
    return 0 if t < 23.4 else 1 if t < 24.9 else 2 if t < 26.8 else 3


class Card:
    def __init__(self, i):
        self.i, self.x = i, 174 + i * 400
        self.ring = El(box(372, CARD_H + 12, 26, None, HIELO, 6))
        self.card = El(box(360, CARD_H, 20, "#ffffff", NIEBLA, 2))
        self.selected = El(box(360, CARD_H, 20, None, AZUL, 2))
        self.img = El(picture(Slide("manimgx-examples", THUMBS[i]).still(), 332, 186, 12))
        self.track = El(box(332, 8, 4, NIEBLA), UL)
        self.done = El(box(332, 8, 4, AZUL), UL)
        self.dots = [El(dot(16, c)) for _, c in STATES]
        colors = [c if 0 < k < 3 else "#0e1116" for k, (_, c) in enumerate(STATES)]
        self.labels = [put(text(s, 28, 500, c), 0, 0) for (s, _), c in zip(STATES, colors)]
        self.mobjects = [self.ring.m, self.card.m, self.selected.m, self.img.m, self.track.m,
                         self.done.m] + [d.m for d in self.dots] + [lb.m for lb in self.labels]

    def look(self, t):
        """Its opacity, how much it rises and its scale."""
        a = 22.7 + self.i * 0.08
        o = out4(p(t, a, a + 0.5)) * (1 - p(t, 28.0, 28.4))
        dy = (1 - out4(p(t, a, a + 0.7))) * 80
        if self.i != 2:
            if 24.8 < t < 27.4:
                o *= 0.35 + 0.65 * (1 - p(t, 24.8, 25.1)) + 0.65 * p(t, 26.9, 27.4)
            return o, dy, 1.0
        lift = out4(p(t, 23.4, 23.9)) * (1 - out4(p(t, 27.3, 27.8)))
        return o, dy - 36 * lift, 1 + 0.08 * lift

    def frame(self, t):
        o, dy, s = self.look(t)
        cx, cy = self.x + 180, 420 + CARD_H / 2 + dy
        mine = self.i == 2
        state = state_at(t) if mine else 0
        sel = mine and t > 23.4

        def at(el, x, y, **kw):  # x, y from the center of the card, scaled with it
            return el.at(cx + x * s, cy + y * s, s=s * kw.pop("k", 1), **kw)

        at(self.ring, 0, 0, o=o if sel else 0)
        at(self.card, 0, 0, o=o)
        at(self.selected, 0, 0, o=o if sel else 0)
        at(self.img, 0, -CARD_H / 2 + 14 + 93, o=o)
        top = -CARD_H / 2 + 14 + 186 + 16
        for k, (d, lb) in enumerate(zip(self.dots, self.labels)):
            at(d, -166 + 8, top + 18, o=o if k == state else 0)
            at(lb, -166 + 28, line(28, top, 1.276) - 2, o=o if k == state else 0)
        bar = top + 36 + 14
        at(self.track, -166, bar, o=o)
        done = p(t, 24.9, 26.8) if mine else 0
        at(self.done, -166, bar, o=o if done > 0 else 0, sx=max(done, 0.001))


def build(scene):
    cards = [Card(i) for i in range(4)]
    first = put(text("Change one slide", 96, spacing=-0.04), 960, line(96, 150), "center")
    second = put(text("Render only that one", 96, spacing=-0.04), 960, line(96, 150), "center")

    def frame(t):
        rise(first, t, 22.6, 960, line(96, 150), 96, 24.4)
        rise(second, t, 24.7, 960, line(96, 150), 96, 28.0)
        for c in cards:
            c.frame(t)

    run(scene, 22.5, 28.5, frame, first.m, second.m, *[m for c in cards for m in c.mobjects])
