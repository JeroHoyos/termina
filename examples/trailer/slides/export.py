"""56.5-62.5 s: present, then export. The slide fills the screen, becomes a card, and five files
fly out of it."""

import math

from manim import VGroup

from kit import (AZUL, GRAFITO, NIEBLA, U, Clip, El, Slide, border, box, inout, lerp, line, out4, p,
                 path, put, reshape, rise, run, text)
from style import HIELO

FILES = ["HTML", "PDF", "MP4", "GIF", "PPTX"]


def tile(name, color):
    """A white tile with a file and its type."""
    icon = VGroup(path("M6 6h50l24 24v68H6z", color), path("M56 6v24h24", HIELO))
    icon.move_to([0, 0.22, 0])
    label = text(name, 34, 500, GRAFITO, 0.08, mono=True)
    label.move_to([0, -0.62, 0])
    return El(VGroup(box(220, 260, 22, "#ffffff", NIEBLA, 2), icon, label))


def build(scene):
    film = Clip(Slide("manimgx-examples", "kaleidoscope_sphere"), 1920, 1080, 0, a=56.5, off=14)
    edge = border(1920, 1080, 0)
    present = put(text("Present", 140, spacing=-0.045), 0, 0)
    card = El(box(present.m.width / U + 88, 140 + 26, 28, "#ffffff"))
    export = put(text("Export", 140, spacing=-0.045), 960, line(140, 70), "center")
    tiles = [tile(f, AZUL if i == 2 else GRAFITO) for i, f in enumerate(FILES)]

    def slide(t):
        sh = inout(p(t, 58.6, 59.3))
        o = p(t, 56.5, 56.8) * (1 - p(t, 62.0, 62.4))
        x, y = lerp(0, 600, sh), lerp(0, 270, sh)
        w, h = lerp(1920, 720, sh), lerp(1080, 405, sh)
        film.show(t, x + w / 2, y + h / 2, s=w / 1920, o=o, r=lerp(0, 20, sh) * 1920 / w)
        reshape(edge, w, h, lerp(0, 20, sh)).at(x + w / 2, y + h / 2, o=o if sh > 0 else 0)
        return sh

    def files(t):
        for i, el in enumerate(tiles):
            a = 59.6 + i * 0.14
            e = out4(p(t, a, a + 0.7))
            x = lerp(850, 330 + i * 260, e)
            y = lerp(370, 740, e) - math.sin(e * math.pi) * 160
            el.at(x + 110, y + 130, s=lerp(0.4, 1, e), r=(1 - e) * (i - 2) * 20,
                  o=(1 if t > a else 0) * (1 - p(t, 62.0, 62.4)))

    def frame(t):
        sh = slide(t)
        o = (1 - sh) * p(t, 56.7, 56.9)
        card.at(120 + card.m.width / U / 2, 800 + 83, o=o)
        leave = inout(p(t, 58.5, 58.9))
        present.at(164, 820 + 140 * 0.846 - 100 * leave, o=o * min(1, out4(p(t, 56.8, 57.4)) * 1.6) * (1 - leave))
        rise(export, t, 59.2, 960, line(140, 70), 140, 62.0)
        files(t)

    run(scene, 56.5, 62.5, frame, film.el.m, edge.m, card.m, present.m, export.m, *[t.m for t in tiles])
