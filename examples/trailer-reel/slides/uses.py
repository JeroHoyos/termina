"""10.5-22.5 s: four ways to use Termina. The words are on top; each device comes in below them
from the right and leaves to the left."""

import math

from manim import UL

from kit import ACERO, AZUL, GRAFITO, HUESO, NIEBLA, El, View, box, line, p, placed, put, rise, run, text
from trailer.uses import USES, Class, Reel, Research, Video, view

X = 90
# The devices of the trailer, smaller: their slide is 810 pixels wide, under the words.
DEVICES = View(dx=540 - 1300, dy=1250 - 482, s=0.78, cx=1300, cy=482)
BOTTOM = 1716  # the bottom of the stage of the trailer, under DEVICES: the people end there


class Words:
    """The number, the word and the line on top, and the four dots of progress."""

    def __init__(self):
        self.nums = [put(text(f"0{i + 1}", 30, 500, AZUL, 0.14, mono=True), X, line(30, 280, 1.276)) for i in range(4)]
        self.words = [put(text(w, 150, spacing=-0.045), X, line(150, 330)) for w, _ in USES]
        self.subs = [put(text(s, 56, 400, ACERO, -0.015), X, line(56, 510, 1.276)) for _, s in USES]
        self.dots = [El(box(64, 10, 5, AZUL), UL) for _ in USES]
        self.mobjects = [e.m for g in (self.nums, self.words, self.subs, self.dots) for e in g]

    def frame(self, t):
        k = min(3, math.floor((t - 10.5) / 3))
        a = 10.5 + k * 3
        for i in range(4):
            on = i == k
            self.nums[i].at(X, line(30, 280, 1.276), o=(p(t, a, a + 0.3) * (1 - p(t, a + 2.75, a + 2.95))) if on else 0)
            if on:
                rise(self.words[i], t, a + 0.05, X, line(150, 330), 150, a + 2.75 if k < 3 else 22.1)
                rise(self.subs[i], t, a + 0.2, X, line(56, 510, 1.276), 56, a + 2.8 if k < 3 else 22.15)
            else:
                self.words[i].at(0, 0, o=0)
                self.subs[i].at(0, 0, o=0)
        self.progress(t, k)

    def progress(self, t, k):
        x, o = X, p(t, 10.6, 11) * (1 - p(t, 22.1, 22.4))
        for i, d in enumerate(self.dots):
            w = 64 if i == k else 20
            d.base.set_fill(AZUL if i == k else GRAFITO if i < k else NIEBLA)
            d.at(x, 620, sx=w / 64, o=o)
            x += w + 16


def build(scene):
    words = Words()
    devices = [Class(), Research(), Reel(), Video()]
    floor = El(box(1080, 1920 - BOTTOM, 0, HUESO), UL)

    def frame(t):
        words.frame(t)
        with placed(DEVICES):
            for i, d in enumerate(devices):
                d.frame(t, view(t, i))
        floor.at(0, BOTTOM)

    run(scene, 10.5, 22.5, frame, *[m for d in devices for m in d.mobjects], floor.m, *words.mobjects)
