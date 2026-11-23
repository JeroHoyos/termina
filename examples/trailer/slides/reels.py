"""62.5-68.5 s: videos and reels. A 16:9 video turns into a 9:16 reel; an equalizer moves with
the real music, and three sound effects pop up as they sound (music.py plays them)."""

from pathlib import Path

from kit import (AZUL, GRAFITO, NIEBLA, Clip, El, Slide, back, border, box, clamp, inout, lerp, line,
                 out4, p, pill, put, reshape, rise, run, text)
from soundkit import meter
from style import HIELO

MUSIC = Path(__file__).resolve().parent.parent / "music.m4a"
START, FPS = 62.5, 60
# The sound effects: their name and when they sound. music.py puts them at the same times.
EFFECTS = [("whoosh", 66.2), ("pop", 66.65), ("click", 67.1)]
# The middle of the space at the right of the reel: the bars, the label and the chips center on it.
CX = (640 + 720 * 9 / 16 / 2 + 1920) / 2


class Effects:
    """A chip for each effect: it pops up, and glows blue while it sounds."""

    def __init__(self):
        self.chips = [(pill(n, 30, 500, GRAFITO, "#ffffff", NIEBLA, 22, 10), pill(n, 30, 500, AZUL, HIELO, AZUL, 22, 10))
                      for n, _ in EFFECTS]
        self.x = []
        x = CX - (sum(w for (_, w, _), _ in self.chips) + 16 * (len(self.chips) - 1)) / 2
        for (_, w, _), _ in self.chips:
            self.x.append(x)
            x += w + 16
        self.mobjects = [el.m for pair in self.chips for el, _, _ in pair]

    def frame(self, t, dx, fade):
        for ((plain, w, h), (lit, _, _)), x, (_, at) in zip(self.chips, self.x, EFFECTS):
            s = back(p(t, at, at + 0.3))
            o = clamp(p(t, at, at + 0.1)) * fade
            glow = 1 - p(t, at + 0.15, at + 0.6)
            for el, alpha in ((plain, 1 - glow), (lit, glow)):
                el.at(x + dx + w / 2 * (1 - s), 790 + h / 2 * (1 - s), s=max(s, 0.001), o=o * alpha)


def build(scene):
    film = Clip(Slide("manimgx-examples", "riemann_surfaces"), 1920, 1080, 28, a=62.5, off=10)
    edge = border(1920, 1080, 28)
    title = put(text("Videos and reels", 96, spacing=-0.04), 960, line(96, 90), "center")
    bars = [El(box(26, 200, 4, AZUL)) for _ in range(14)]
    label = put(text("Music and sound effects", 48, 500, GRAFITO, -0.015), CX, line(48, 695, 1.276), "center")
    levels = meter(MUSIC, START - 4.0, 6.0, FPS, len(bars))  # the music has no find scene (music.py)
    effects = Effects()

    def reel(t):
        m = inout(p(t, 64.0, 65.0))
        h = lerp(560, 720, m)
        w = lerp(h * 16 / 9, h * 9 / 16, m)
        cx = lerp(960, 640, inout(p(t, 65.0, 65.8)))
        o = out4(p(t, 62.5, 63.0)) * (1 - p(t, 68.0, 68.4))
        film.show(t, cx, 250 + 360, w=w, h=h, o=o, zoom=lerp(1, 1.6, m))
        reshape(edge, w, h, 28).at(cx, 250 + 360, o=o)

    def music(t):
        on = p(t, 65.4, 65.9) * (1 - p(t, 67.9, 68.3))
        dx = (1 - out4(p(t, 65.4, 66.0))) * 60
        row = levels[min(len(levels) - 1, max(0, round((t - START) * FPS)))]
        for i, b in enumerate(bars):
            hgt = max(8, (0.15 + 0.85 * row[i]) * 200 * on)
            b.at(CX - (len(bars) * 38 - 12) / 2 + dx + i * 38 + 13, 675 - hgt / 2, sy=hgt / 200, o=on)
        label.at(CX, line(48, 695, 1.276), o=on)
        effects.frame(t, dx, 1 - p(t, 67.9, 68.3))

    def frame(t):
        rise(title, t, 62.6, 960, line(96, 90), 96, 68.0)
        reel(t)
        music(t)

    run(scene, 62.5, 68.5, frame, title.m, film.el.m, edge.m, *[b.m for b in bars], label.m,
        *effects.mobjects)
