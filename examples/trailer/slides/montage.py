"""4.5-10.5 s: big words over the films, cut on the beat."""

from kit import AZUL, HUESO, Clip, El, Slide, back, box, clamp, lerp, out4, p, put, run, text

# film, from, to, the second of the film at `from`
CUTS = [("kaleidoscope_sphere", 4.5, 5.5, 12), ("turing_torus", 5.5, 6.5, 15),
        ("clifford_torus", 6.5, 7.5, 15), ("riemann_surfaces", 7.5, 8.0, 14),
        ("sphere_packing", 8.0, 8.5, 16), ("hilbert_curve", 8.5, 9.0, 12),
        ("surface_plots", 9.0, 9.5, 9), ("taylor_poles", 9.5, 10.0, 16), ("times_tables", 10.0, 10.5, 10)]
WORDS = [("Talks", 4.5, 5.5), ("Videos", 5.5, 6.5), ("Reels", 6.5, 7.5), ("Made with math", 7.5, 10.5)]


class Word:
    """A big word with a soft glow of the background color, so it reads over a film."""

    def __init__(self, s, a, b):
        self.a, self.b = a, b
        self.size = 180 if s == "Made with math" else 220
        self.y = 420 + self.size * 0.846  # the baseline of a line 1 em high at 420 px
        glow = text(s, self.size, spacing=-0.05, color=HUESO).set_stroke(HUESO, width=26, opacity=0.4)
        sharp = text(s, self.size, spacing=-0.05)
        glow.baseline = sharp.baseline
        self.els = [put(glow, 960, self.y, "center"), put(sharp, 960, self.y, "center")]

    def frame(self, t):
        on = self.a <= t < self.b or (self.b == 10.5 and t >= self.b)
        pop = back(p(t, self.a, self.a + 0.3))
        s = lerp(0.85, 1, pop) + 0.04 * p(t, self.a, self.b)
        o = clamp(pop) * (1 - p(t, 10.1, 10.4)) if on else 0
        for el in self.els:
            el.at(960, self.y, s=s, o=o)


def films(t, cuts):
    fade = 1 - p(t, 10.15, 10.5)
    for clip, (_, a, b, _) in zip(cuts, CUTS):
        if a <= t < b:
            clip.show(t, 960, 540, o=fade, zoom=1.42 - 0.08 * out4(p(t, a, b + 0.3)))
        else:
            clip.el.at(0, 0, o=0)


def bar(t, wipe):
    """A blue bar crosses the frame at each cut."""
    cut = next((c for c in CUTS if c[1] - 0.12 <= t < c[1] + 0.12 and c[1] > 4.6), None)
    x = lerp(-200, 1960, p(t, cut[1] - 0.12, cut[1] + 0.12)) if cut else 0
    wipe.at(x + 80, 540, o=1 if cut else 0)


def build(scene):
    cuts = [Clip(Slide("manimgx-examples", n), 1920, 1080, a=a, off=off) for n, a, _, off in CUTS]
    words = [Word(*w) for w in WORDS]
    wipe = El(box(160, 1080, 0, AZUL))

    def frame(t):
        films(t, cuts)
        bar(t, wipe)
        for w in words:
            w.frame(t)

    run(scene, 4.5, 10.5, frame, *[c.el.m for c in cuts], wipe.m, *[el.m for w in words for el in w.els])
