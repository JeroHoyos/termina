"""56.5-62.5 s: present, then export. The slide fills the phone, becomes a card, and five files
fly out of it into a row."""

import math

from kit import (AZUL, GRAFITO, U, Clip, El, Slide, border, box, inout, lerp, line, out4, p, put,
                 reshape, rise, run, text)
from trailer.export import FILES, tile

CARD = (60, 520, 960, 540)  # where the slide ends: x, y, w, h


def build(scene):
    film = Clip(Slide("manimgx-examples", "kaleidoscope_sphere"), 1080, 1920, 0, a=56.5, off=14)
    edge = border(1080, 1920, 0)
    present = put(text("Present", 150, spacing=-0.045), 0, 0)
    card = El(box(present.m.width / U + 88, 150 + 26, 28, "#ffffff"))
    export = put(text("Export", 160, spacing=-0.045), 540, line(160, 300), "center")
    tiles = [tile(f, AZUL if i == 2 else GRAFITO) for i, f in enumerate(FILES)]

    def slide(t):
        sh = inout(p(t, 58.6, 59.3))
        o = p(t, 56.5, 56.8) * (1 - p(t, 62.0, 62.4))
        x, y, w, h = (lerp(a, b, sh) for a, b in zip((0, 0, 1080, 1920), CARD))
        film.show(t, x + w / 2, y + h / 2, w=w, h=h, o=o, r=lerp(0, 20, sh), zoom=lerp(1.4, 1, sh))  # the title shows on the card
        reshape(edge, w, h, lerp(0, 20, sh)).at(x + w / 2, y + h / 2, o=o if sh > 0 else 0)
        return sh

    def files(t):
        for i, el in enumerate(tiles):
            a = 59.6 + i * 0.14
            e = out4(p(t, a, a + 0.7))
            x = lerp(540, 148 + i * 196, e)
            y = lerp(790, 1250, e) - math.sin(e * math.pi) * 160
            el.at(x, y, s=lerp(0.3, 0.8, e), r=(1 - e) * (i - 2) * 20,
                  o=(1 if t > a else 0) * (1 - p(t, 62.0, 62.4)))

    def frame(t):
        sh = slide(t)
        o = (1 - sh) * p(t, 56.7, 56.9)
        card.at(90 + card.m.width / U / 2, 1380 + 88, o=o)
        leave = inout(p(t, 58.5, 58.9))
        present.at(134, 1400 + 150 * 0.846 - 100 * leave, o=o * min(1, out4(p(t, 56.8, 57.4)) * 1.6) * (1 - leave))
        rise(export, t, 59.2, 540, line(160, 300), 160, 62.0)
        files(t)

    run(scene, 56.5, 62.5, frame, film.el.m, edge.m, card.m, present.m, export.m, *[t.m for t in tiles])
