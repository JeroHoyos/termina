"""The 48 example films of ManimGX, one on each slide.

TRAILER COPY: every paint is relit for the light GRADIENT look (Hueso background): neutral
colors turn over (white text becomes Grafito, dark grid lines become light), and bright colors
get darker so they read on a light page.
"""

import numpy as np

import manimgx as m
from manimgx.config import config

HUESO = np.array([246, 246, 243]) / 255
GRAFITO = np.array([14, 17, 22]) / 255
MARK = np.array([-0.012, 0, 0])  # a relit gray is a little less red than the line


def relight(rgba):
    if rgba is None or len(rgba) == 0:
        return rgba
    a = np.array(rgba, dtype=float)
    rgb = a[:, :3]
    hi, lo = rgb.max(1), rgb.min(1)
    light = (hi + lo) / 2
    s = (rgb[:, 1:2] - GRAFITO[1]) / (HUESO[1] - GRAFITO[1])
    done = np.abs(GRAFITO + (HUESO - GRAFITO) * s + MARK - rgb).max(1) < 0.002  # already relit
    neutral = ((hi - lo) < 0.14) & ~done
    flipped = GRAFITO + (HUESO - GRAFITO) * (0.9 * (1 - light))[:, None] + MARK
    luma = rgb @ np.array([0.299, 0.587, 0.114])
    darker = rgb * np.minimum(1, 0.58 / np.maximum(luma, 1e-6))[:, None]
    a[:, :3] = np.where(neutral[:, None], flipped, np.where(done[:, None], rgb, darker))
    return a


def _get(self):
    return self.__dict__["_lit"]


def _set(self, paint):
    try:
        changes = {k: relight(getattr(paint, "_" + k)) for k in ("fill", "stroke")
                   if getattr(paint, "_" + k, None) is not None}
        if changes and getattr(paint, "mix", None) is None:
            paint = paint.but(**changes)
    except Exception:
        pass
    self.__dict__["_lit"] = paint


m.Mobject.paint = property(_get, _set)


def play(scene, film):
    for mob in scene.mobjects:
        mob.clear_updaters()
    scene.clear()
    scene.updaters.clear()
    talk, start = scene.__class__, scene.time
    scene.__class__ = type(film.__name__, (film, talk),
                           {"time": property(lambda s: talk.time.fget(s) - start)})
    config.background_color = m.ManimColor("#f6f6f3")
    scene.camera = m.Camera(three_d=film.three_d)
    try:
        film.construct(scene)
    finally:
        scene.__class__ = talk
    scene.next_slide()
