"""32.5-46.5 s: six ways to guide a slide. The step is a big word on top; the slide and the bar
of the note of the trailer are under it, at 80 %."""

from kit import (AZUL, Clip, El, Slide, View, border, cursor, dot, keyframes, lerp, line, out4, p,
                 placed, put, ring, ripple, rise, run, text)
from trailer.guide import STEPS, Marks, Note, keys, light

SLIDE = View(dx=540 - 960, dy=1060 - 590, s=0.8, cx=960, cy=590)


class Steps:
    def __init__(self):
        self.words = [put(text(w, 120, spacing=-0.04), 540, line(120, 400), "center") for w, _ in STEPS]
        self.dots = [(El(dot(22, None, AZUL, 3)), El(dot(22, AZUL))) for _ in STEPS]
        self.mobjects = [w.m for w in self.words] + [d.m for pair in self.dots for d in pair]

    def frame(self, t):
        k = max([i for i, (_, a) in enumerate(STEPS) if t >= a] or [0])
        a = STEPS[k][1]
        for i, w in enumerate(self.words):
            if i == k:
                rise(w, t, a + 0.02, 540, line(120, 400), 120, a + 1.75 if k < 5 else 45.9, 0.45)
            else:
                w.at(0, 0, o=0)
        self.progress(t, k, a)

    def progress(self, t, k, a):
        o = p(t, 32.6, 33) * (1 - p(t, 45.9, 46.3))
        for i, (empty, full) in enumerate(self.dots):
            s = 1 + 0.3 * (1 - out4(p(t, a, a + 0.4))) if i == k else 1
            x = 540 + (i - 2.5) * 40
            empty.at(x, 600, s=s, o=o)
            full.at(x, 600, s=s, o=o if i <= k else 0)


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
        with placed(SLIDE):
            film.show(t, 960, 510, s=s * 2 / 3, o=o)
            edge.at(960, 510, s=s, o=o)
            marks.frame(t, o)
            note.frame(t)
        x, y = SLIDE.xy(*keyframes(t, path_keys))
        down = any(c < t < c + 0.18 for c in clicks)
        arrow.at(x, y, s=0.85 if down else 1, o=p(t, 32.8, 33.0) * (1 - p(t, 45.8, 46.0)))
        last = max([c for c in clicks if t > c - 0.5] or [33.5])
        ripple(rip, t, last, x + 8, y + 6)

    run(scene, 32.5, 46.5, frame, film.el.m, edge.m, *marks.mobjects, *note.mobjects,
        *steps.mobjects, arrow.m, rip.m)
