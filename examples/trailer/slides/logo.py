"""0-4.5 s: the T of the logo builds itself, the word draws, and its blue dot opens like an
iris on the first film."""

import numpy as np
from manim import CapStyleType, Circle, ImageMobject, LineJointType, config

from kit import (H, P, W, AZUL, GRAFITO, El, Slide, U, _rgba, box, clamp, inout, lerp, out4, back, p,
                 path, run, set_pixels, sw)

# The logo in the units of its SVG (1770 x 512), drawn at 0.586: 1037 x 300 pixels at (810, 340).
K = 1037 / 1770
LETTERS = ["M524 235H668A72 72 0 1 0 647 286", "M764 307V163M764 235A72 72 0 0 1 836 163H854",
           "M950 307V163M950 215A52 52 0 0 1 1054 215V307M1054 215A52 52 0 0 1 1158 215V307",
           "M1254 307V163", "M1350 307V163M1350 235A72 72 0 0 1 1494 235V307",
           "M1734 235A72 72 0 1 0 1590 235A72 72 0 1 0 1734 235M1734 163V307"]
FILM = ("manimgx-examples", "kaleidoscope_sphere")


def letters(k=K):
    out = []
    for d in LETTERS:
        m = path(d, stroke=GRAFITO, width=46 * k, scale=k)
        m.set_cap_style(CapStyleType.ROUND)
        m.joint_type = LineJointType.ROUND
        out.append(m)
    return out


class Logo:
    """The T builds at (x, y), then moves by `shift` to make room for the word. `k` is its size."""

    def __init__(self, k=K, x=810, y=340, shift=-376):
        self.k, self.x, self.y, self.shift = k, x, y, shift
        self.bar, self.stem = El(box(10, 10)), El(box(10, 10))
        self.dot, self.idot = El(box(10, 10)), El(box(10, 10))
        self.words = [(m, m.copy()) for m in letters(k)]
        self.parts = [self.stem.m, self.bar.m, self.dot.m] + [m for m, _ in self.words] + [self.idot.m]

    def xy(self, x, y, dx):
        """A point of the SVG on the stage."""
        return self.x + dx + x * self.k, self.y + y * self.k

    def rect(self, el, x, y, w, h, color, o, dx):
        el.m.become(box(w * self.k, h * self.k, 50 * self.k, color))
        el.base = el.m.copy()
        el.at(*self.xy(x + w / 2, y + h / 2, dx), o=o)

    def circle(self, el, cx, cy, r, color, dx):
        r = max(r, 0.5)
        el.m.become(box(2 * r * self.k, 2 * r * self.k, r * self.k, color))
        el.base = el.m.copy()
        el.at(*self.xy(cx, cy, dx), o=1 if r > 0.5 else 0)

    def frame(self, t):
        dx = self.shift * inout(p(t, 2.2, 3.0))
        fall = p(t, 0.35, 1.0)
        squash = 0.2 * np.sin(p(t, 1.0, 1.2) * np.pi) if t > 1.0 else 0
        self.circle(self.dot, 256, 422 - 520 * (1 - fall * fall), 56 * (1 - squash * 0.3), AZUL, dx)
        g = out4(p(t, 1.0, 1.25))
        top = lerp(335, 40, g) - 50 * (1 - g)
        self.rect(self.stem, 206, top, 100, max(100, 335 - top), GRAFITO, 1 if t > 1.0 else 0, dx)
        b = out4(p(t, 1.5, 1.75))
        self.rect(self.bar, lerp(206, 56, b), 40, lerp(100, 400, b), 100, GRAFITO, 1 if t > 1.5 else 0, dx)
        self.draw_words(t, dx)
        self.circle(self.idot, 1238, 84, 30 * clamp(back(p(t, 3.15, 3.45)), 0, 2), AZUL, dx)

    def draw_words(self, t, dx):
        for i, (m, whole) in enumerate(self.words):
            e = inout(p(t, 2.45 + i * 0.09, 3.0 + i * 0.09))
            m.pointwise_become_partial(whole.copy().shift(P(*self.xy(-16, 0, dx))), 0, max(e, 1e-4))
            m.set_stroke(opacity=1 if e > 0 else 0)


class Iris:
    """The blue dot of the T grows into a circle, with the first film inside it."""

    def __init__(self, logo):
        self.logo = logo
        self.film = Slide(*FILM)
        self.img = ImageMobject(np.zeros((4, 4, 4), np.uint8))
        self.ring = El(Circle(radius=1).set_stroke(AZUL, sw(20)))

    def frame(self, t):
        f = inout(p(t, 3.8, 4.5))
        on = t > 3.8
        self.ring.at(0, 0, o=0)
        if not on:
            set_pixels(self.img, np.zeros((4, 4, 4), np.uint8))
            return
        cx, cy = self.logo.xy(256, 422, self.logo.shift)
        r = lerp(56 * self.logo.k, 2300, f)
        rgba = _rgba(self.film.frame(9 + (t - 3.8)), W, H, zoom=1.3)
        k = config.pixel_width / W
        yy, xx = np.mgrid[0:rgba.shape[0], 0:rgba.shape[1]] + 0.5
        inside = np.clip(r * k - np.hypot(xx - cx * k, yy - cy * k) + 0.5, 0, 1)
        rgba[..., 3] = (inside * 255).astype(np.uint8)
        set_pixels(self.img, rgba)
        self.img.stretch_to_fit_width(W * U).stretch_to_fit_height(H * U).move_to(P(W / 2, H / 2))
        width = lerp(20, 0, f)
        self.ring.base.set_stroke(width=sw(width)).scale_to_fit_width(2 * r * U)
        self.ring.at(cx, cy, o=1 if width > 0.2 else 0)


def build(scene, logo=None):
    logo = logo or Logo()
    iris = Iris(logo)

    def frame(t):
        logo.frame(t)
        iris.frame(t)

    run(scene, 0, 4.5, frame, *logo.parts, iris.img, iris.ring.m)
