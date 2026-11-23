"""62.5-68.5 s: videos and reels. A 16:9 video turns into a 9:16 reel; under it an equalizer moves
with the real music, and three sound effects pop up as they sound (music.py plays them)."""

from kit import (AZUL, GRAFITO, Clip, El, Slide, View, border, box, inout, lerp, line, out4, p, placed,
                 put, reshape, rise, run, text)
from soundkit import meter
from trailer.reels import CX, FPS, MUSIC, START, Effects

CY = 860  # the center of the video


def build(scene):
    film = Clip(Slide("manimgx-examples", "riemann_surfaces"), 960, 540, 28, a=62.5, off=10)
    edge = border(960, 540, 28)
    title = put(text("Videos and reels", 120, spacing=-0.04), 540, line(120, 240), "center")
    bars = [El(box(26, 170, 4, AZUL)) for _ in range(14)]
    label = put(text("Music and sound effects", 52, 500, GRAFITO, -0.015), 540, line(52, 1460, 1.276), "center")
    levels = meter(MUSIC, START - 4.0, 6.0, FPS, len(bars))  # the music has no find scene (music.py)
    effects = Effects()

    def reel(t):
        m = inout(p(t, 64.0, 65.0))
        h = lerp(540, 760, m)
        w = lerp(h * 16 / 9, h * 9 / 16, m)
        o = out4(p(t, 62.5, 63.0)) * (1 - p(t, 68.0, 68.4))
        film.show(t, 540, CY, w=w, h=h, o=o, zoom=lerp(1, 1.6, m))
        reshape(edge, w, h, 28).at(540, CY, o=o)

    def music(t):
        on = p(t, 65.4, 65.9) * (1 - p(t, 67.9, 68.3))
        dy = (1 - out4(p(t, 65.4, 66.0))) * 60
        row = levels[min(len(levels) - 1, max(0, round((t - START) * FPS)))]
        for i, b in enumerate(bars):
            hgt = max(8, (0.15 + 0.85 * row[i]) * 170 * on)
            b.at(540 - 260 + i * 38 + 13, 1420 + dy - hgt / 2, sy=hgt / 170, o=on)
        label.at(540, line(52, 1460, 1.276) + dy, o=on)
        with placed(View(dx=540 - CX, dy=1560 - 790 + dy)):  # the chips of the trailer: on CX, at y = 790
            effects.frame(t, 0, 1 - p(t, 67.9, 68.3))

    def frame(t):
        rise(title, t, 62.6, 540, line(120, 240), 120, 68.0)
        reel(t)
        music(t)

    run(scene, 62.5, 68.5, frame, title.m, film.el.m, edge.m, *[b.m for b in bars], label.m, *effects.mobjects)
