"""4.5-10.5 s: big words over the films, cut on the beat. The films fill the phone."""

from kit import AZUL, HUESO, Clip, El, Slide, back, box, clamp, lerp, out4, p, put, run, text
from trailer.montage import CUTS, WORDS


class Word:
    """A big word (or two lines) with a soft glow of the background color, so it reads over a film."""

    def __init__(self, s, a, b):
        self.a, self.b = a, b
        lines = ["Made with", "math"] if s == "Made with math" else [s]
        size = 200 if len(lines) > 1 else 230
        top = 960 - len(lines) * size / 2
        self.els = []
        for i, words in enumerate(lines):
            y = top + i * size + size * 0.846
            glow = text(words, size, spacing=-0.05, color=HUESO).set_stroke(HUESO, width=26, opacity=0.4)
            sharp = text(words, size, spacing=-0.05)
            glow.baseline = sharp.baseline
            self.els += [(put(glow, 540, y, "center"), y), (put(sharp, 540, y, "center"), y)]

    def frame(self, t):
        on = self.a <= t < self.b or (self.b == 10.5 and t >= self.b)
        pop = back(p(t, self.a, self.a + 0.3))
        s = lerp(0.85, 1, pop) + 0.04 * p(t, self.a, self.b)
        o = clamp(pop) * (1 - p(t, 10.1, 10.4)) if on else 0
        for el, y in self.els:
            el.at(540, 960 + (y - 960) * s, s=s, o=o)


def films(t, cuts):
    fade = 1 - p(t, 10.15, 10.5)
    for clip, (_, a, b, _) in zip(cuts, CUTS):
        if a <= t < b:
            clip.show(t, 540, 960, o=fade, zoom=1.42 - 0.08 * out4(p(t, a, b + 0.3)))  # no title of the slide
        else:
            clip.el.at(0, 0, o=0)


def bar(t, wipe):
    """A blue bar crosses the frame from top to bottom at each cut."""
    cut = next((c for c in CUTS if c[1] - 0.12 <= t < c[1] + 0.12 and c[1] > 4.6), None)
    y = lerp(-200, 2120, p(t, cut[1] - 0.12, cut[1] + 0.12)) if cut else 0
    wipe.at(540, y, o=1 if cut else 0)


def build(scene):
    cuts = [Clip(Slide("manimgx-examples", n), 1080, 1920, a=a, off=off) for n, a, _, off in CUTS]
    words = [Word(*w) for w in WORDS]
    wipe = El(box(1080, 160, 0, AZUL))

    def frame(t):
        films(t, cuts)
        bar(t, wipe)
        for w in words:
            w.frame(t)

    run(scene, 4.5, 10.5, frame, *[c.el.m for c in cuts], wipe.m, *[el.m for w in words for el, _ in w.els])
