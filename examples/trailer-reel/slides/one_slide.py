"""22.5-28.5 s: change one slide, render only that one. The four cards of the trailer, in two
rows of two."""

from kit import View, line, placed, put, rise, run, text
from trailer.one_slide import CARD_H, Card

S = 1.15
CENTERS = [(318, 830), (762, 830), (318, 1206), (762, 1206)]


def build(scene):
    cards = [Card(i) for i in range(4)]
    for c in cards:
        c.x = 0  # its center is at (180, 420 + CARD_H / 2) of the trailer; the views move it
    views = [View(dx=x - 180, dy=y - (420 + CARD_H / 2), s=S, cx=180, cy=420 + CARD_H / 2) for x, y in CENTERS]
    first = put(text("Change one slide", 100, spacing=-0.04), 540, line(100, 440), "center")
    second = put(text("Render only that one", 100, spacing=-0.04), 540, line(100, 440), "center")

    def frame(t):
        rise(first, t, 22.6, 540, line(100, 440), 100, 24.4)
        rise(second, t, 24.7, 540, line(100, 440), 100, 28.0)
        for c, v in zip(cards, views):
            with placed(v):
                c.frame(t)

    run(scene, 22.5, 28.5, frame, first.m, second.m, *[m for c in cards for m in c.mobjects])
