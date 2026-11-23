"""The tools of the trailer: a stage in pixels of 1920 x 1080 (1080 x 1920 for a reel), a
clock, text, boxes, and the videos of slides of other talks.

Each scene is a function of the time `t` of the whole trailer, in seconds: `run` moves a clock
from the start of the scene to its end, and each frame puts every object where it must be at
that time. The cuts fall on the beat of the music because the scenes have exact lengths.
"""

import json
import math
import re
from contextlib import contextmanager
from pathlib import Path

import av
import numpy as np
from manim import (DL, DOWN, LEFT, ORIGIN, UL, UP, Group, ImageMobject, Mobject, RoundedRectangle, VGroup,
                   Text, ValueTracker, VMobject, config, linear)
from PIL import Image

from style import ACERO, AZUL, GRAFITO, HUESO, NIEBLA

W, H = (1080, 1920) if config.frame_height > config.frame_width else (1920, 1080)  # the stage
U = config.frame_width / W  # one pixel of the stage, in Manim units
EXAMPLES = Path(__file__).resolve().parent.parent
GX = ImageMobject.__module__.startswith("manimgx")  # ManimGX draws, in place of Manim CE


def set_pixels(img, rgba):
    """Gives a picture new pixels (RGBA)."""
    if GX:
        img.paint = img.paint.but(texture=rgba)
    else:
        img.pixel_array = rgba


def P(x, y):
    """The point of the stage at (x, y) pixels from the top left corner (moved by `placed`)."""
    x, y = STAGE.xy(x, y)
    return np.array([(x - W / 2) * U, (H / 2 - y) * U, 0.0])


def sw(px):
    """A stroke width of `px` pixels."""
    return px * U / 0.01


# ── time ──

def clamp(x, a=0.0, b=1.0):
    return min(b, max(a, x))


def p(t, a, b):
    """0 before a, 1 after b, linear between."""
    return clamp((t - a) / (b - a))


def out4(x):
    return 1 - (1 - clamp(x)) ** 4


def inout(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def back(x):
    x = clamp(x)
    return 1 + 2.7 * (x - 1) ** 3 + 1.7 * (x - 1) ** 2


def lerp(a, b, x):
    return a + (b - a) * x


def blink(t):
    return 1 if math.floor(t * 2.5) % 2 == 0 else 0


def typed(text, t, a, b):
    return text[:math.floor(p(t, a, b) * len(text))]


def run(scene, a, b, frame, *mobjects):
    """Plays the scene from second `a` to second `b` of the trailer. `frame(t)` puts the objects
    in place for each frame. At the end the stage is empty: the next scene starts on a cut."""
    clock = ValueTracker(a)
    stage = Group(*mobjects)
    stage.add_updater(lambda _: frame(clock.get_value()))
    frame(a)
    scene.add(stage)
    scene.play(clock.animate.set_value(b), run_time=b - a, rate_func=linear)
    stage.clear_updaters()
    scene.remove(*scene.mobjects)


# ── objects that change each frame ──

class El:
    """An object of the stage. `at` puts its anchor at a point in pixels, with a scale, an
    opacity and a rotation, always from the object as it was made."""

    def __init__(self, m, anchor=ORIGIN, origin=None):
        self.m = m
        self.base = m.copy()
        point = self.base.get_critical_point(anchor) if origin is None else origin
        self.anchor = point - self.base.get_center()

    def at(self, x, y, s=1.0, o=1.0, r=0.0, sx=1.0, sy=1.0):
        m = self.m
        if isinstance(m, ImageMobject) and not GX:  # its pixels can change size, become() can not do that
            m.pixel_array, m.points = self.base.pixel_array.copy(), self.base.points.copy()
        else:
            m.become(self.base)
        s, o = s * STAGE.s, o * STAGE.o
        if s * sx * sy == 0 or o <= 0.002:
            fade(m, 0)
            return m
        if (s, sx, sy) != (1, 1, 1):
            m.stretch(s * sx, 0).stretch(s * sy, 1)
        if r:
            m.rotate(math.radians(-r))
        m.move_to(P(x, y) - self.anchor * np.array([s * sx, s * sy, 1]))
        fade(m, o)
        return m


class View:
    """A group that moves by (dx, dy) and scales by `s` around (cx, cy), with an opacity: like
    the CSS transform of a box that holds other boxes."""

    def __init__(self, dx=0.0, dy=0.0, s=1.0, cx=960.0, cy=540.0, o=1.0):
        self.dx, self.dy, self.s, self.cx, self.cy, self.o = dx, dy, s, cx, cy, o

    def xy(self, x, y):
        return self.cx + (x - self.cx) * self.s + self.dx, self.cy + (y - self.cy) * self.s + self.dy

    def at(self, el, x, y, s=1.0, o=1.0, **kw):
        return el.at(*self.xy(x, y), s=s * self.s, o=o * self.o, **kw)

    def show(self, clip, t, x, y, s=1.0, o=1.0, **kw):
        return clip.show(t, *self.xy(x, y), s=s * self.s, o=o * self.o, **kw)


STAGE = View()


@contextmanager
def placed(view):
    """Everything drawn in this block moves and scales by `view`: a part of a scene of the
    trailer, put in another place of the stage of the reel."""
    global STAGE
    old, STAGE = STAGE, view
    try:
        yield
    finally:
        STAGE = old


def fade(m, o):
    """Multiplies the opacity of each part by `o` (a box with no fill keeps no fill)."""
    if o >= 0.999:
        return
    for sm in m.get_family():
        if isinstance(sm, VMobject):
            sm.set_fill(opacity=sm.get_fill_opacity() * o, family=False)
            sm.set_stroke(opacity=sm.get_stroke_opacity() * o, family=False)
        elif isinstance(sm, ImageMobject):
            if GX:
                sm.set_opacity(o, family=False)
            else:
                sm.pixel_array = (sm.pixel_array * np.array([1, 1, 1, o])).astype(np.uint8)


def box(w, h, r=0, fill=None, stroke=None, width=2):
    """A box of w x h pixels with round corners of radius r."""
    b = RoundedRectangle(width=w * U, height=h * U, corner_radius=max(0.001, min(r, w / 2, h / 2)) * U)
    b.set_fill(fill or "#ffffff", opacity=1 if fill else 0)
    b.set_stroke(stroke or "#ffffff", width=sw(width), opacity=1 if stroke else 0)
    return b


def border(w, h, r=20, color=NIEBLA, width=2):
    """The thin line around a frame: an El anchored at its center."""
    return El(box(w, h, r, None, color, width))


def reshape(el, w, h, r, color=NIEBLA, width=2):
    """Gives a frame line a new size, with round corners of the same radius."""
    el.base = box(w, h, r, None, color, width)
    return el


def dot(d, color, stroke=None, width=3):
    return box(d, d, d / 2, color, stroke, width)


def path(d, fill=None, stroke=None, width=2, scale=1.0):
    """A shape from the `d` of an SVG path, in pixels (y down), with its own origin at (0, 0)."""
    from manim import VMobjectFromSVGPath
    from svgelements import Path as SvgPath
    m = VMobjectFromSVGPath(SvgPath(d))
    m.stretch(-1, 1, about_point=ORIGIN)  # svg y goes down
    m.scale(U * scale, about_point=ORIGIN)
    m.set_fill(fill or "#ffffff", opacity=1 if fill else 0)
    m.set_stroke(stroke or "#ffffff", width=sw(width) if stroke else 0, opacity=1 if stroke else 0)
    return m


CURSOR = "M8 4 L8 46 L19 35 L27 52 L35 48 L27 32 L42 32 Z"


def cursor():
    """The arrow of the mouse. Its anchor is the top left of its 56 px box."""
    return El(path(CURSOR, GRAFITO, "#ffffff", 3), origin=ORIGIN)


def keyframes(t, keys):
    """A point along [(t, x, y), …], eased between the keys."""
    if t <= keys[0][0]:
        return keys[0][1:]
    for (a, x1, y1), (b, x2, y2) in zip(keys, keys[1:]):
        if t < b:
            e = inout(p(t, a, b))
            return lerp(x1, x2, e), lerp(y1, y2, e)
    return keys[-1][1:]


def ripple(el, t, at, x, y, size=110):
    """A blue ring that opens where the cursor clicks."""
    e = p(t, at, at + 0.45)
    r = size * out4(e)
    el.at(x, y, s=max(r, 0.01) / 100, o=1 - e if 0 < e < 1 else 0)


def ring():
    return El(dot(100, None, AZUL, 5).set_fill(opacity=0))


def rise(el, t, a, x, y, size, z=1e9, d=0.6, s=1.0):
    """A line of text that rises into its place at `a` and leaves upward at `z`."""
    i, o = out4(p(t, a, a + d)), inout(p(t, z, z + 0.4))
    el.at(x, y + size * 0.7 * ((1 - i) - o), s=s, o=clamp(i * 1.6) * (1 - o))


# ── text ──

WEIGHTS = {400: "NORMAL", 500: "MEDIUM", 600: "SEMIBOLD", 700: "BOLD"}
_CAP = {}


def text(s, size, weight=600, color=GRAFITO, spacing=0.0, mono=False, font=None):
    """Text whose capital letters are 0.7 x size pixels high, as in a browser. `spacing` is the
    letter spacing in em. Its anchor is its baseline (see `put`)."""
    font = font or ("IBM Plex Mono" if mono else "Space Grotesk")
    key = (font, weight)
    # ManimGX reads the fonts of the trailer from their folder; for Manim CE, style.py registers them
    fonts = {"font_paths": [Path(__file__).parent / "fonts"]} if GX else {}
    if key not in _CAP:
        _CAP[key] = Text("H", font=font, weight=WEIGHTS[weight], font_size=100, **fonts).height / 100
    m = Text(s, font=font, weight=WEIGHTS[weight], font_size=100, color=color, disable_ligatures=True, **fonts)
    m.scale(0.7 * size * U / (_CAP[key] * 100))
    # One part for each character, or for each character that is not a space.
    pairs = list(zip(m.submobjects, s if len(m.submobjects) == len(s) else [c for c in s if not c.isspace()]))
    for i, (g, _) in enumerate(pairs if spacing else []):
        g.shift(LEFT * -i * spacing * size * U)
    m.baseline = _baseline(m, pairs) - m.get_center()[1]
    return m


def _baseline(m, pairs):
    """The bottom of the letters that do not go below the line."""
    bottoms = [g.get_bottom()[1] for g, ch in pairs if not ch.isspace() and ch not in "gjpqy,;()"]
    return min(bottoms, default=m.get_bottom()[1])


def put(m, x, y, align="left"):
    """An El of the text, anchored at its baseline: at `align` (left, center, right) of x."""
    side = {"left": LEFT, "center": ORIGIN, "right": -LEFT}[align]
    el = El(m)
    el.anchor = np.array([side[0] * m.width / 2, m.baseline, 0])
    el.at(x, y)
    return el


def line(size, top, height=1.0):
    """The baseline of a line of text at `top` pixels, with a line height of `height` em."""
    return top + size * ((height - 1.276) / 2 + 0.984)


# ── pictures and the videos of slides ──

def _rounded(w, h, r, circle=False):
    """The alpha of a picture of w x h with round corners (or a circle)."""
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    if circle:
        d = np.hypot(xx - w / 2, yy - h / 2) - min(w, h) / 2
    else:
        qx = np.maximum(np.abs(xx - w / 2) - (w / 2 - r), 0)
        qy = np.maximum(np.abs(yy - h / 2) - (h / 2 - r), 0)
        d = np.hypot(qx, qy) - r
    return np.clip(0.5 - d, 0, 1)


def picture(rgb, w, h, r=0, circle=False):
    """An ImageMobject of w x h pixels from an RGB array (cropped to fill, like object-fit: cover)."""
    img = ImageMobject(_rgba(rgb, w, h, r, circle))
    img.stretch_to_fit_width(w * U).stretch_to_fit_height(h * U)
    return img


def _rgba(rgb, w, h, r=0, circle=False, zoom=1.0):
    """The picture at the resolution of the render (w, h and r are in pixels of the stage)."""
    k = config.pixel_width / W
    w, h, r = max(2, round(w * k)), max(2, round(h * k)), r * k
    src = Image.fromarray(rgb)
    k = max(w / src.width, h / src.height) * zoom
    cw, ch = w / k, h / k
    left, top = max(0.0, (src.width - cw) / 2), max(0.0, (src.height - ch) / 2)
    cw, ch = min(cw, src.width - left), min(ch, src.height - top)
    out = np.asarray(src.resize((w, h), Image.LANCZOS, box=(left, top, left + cw, top + ch)))
    alpha = (_rounded(w, h, r, circle) * 255) if (r or circle) else np.full((h, w), 255.0)
    return np.dstack([out, alpha]).astype(np.uint8)


class Slide:
    """The video of a rendered slide of another talk, as one clip: its parts one after the other.
    The talk renders it: the trailer only reads its .termina folder."""

    def __init__(self, talk, name):
        folder = EXAMPLES / talk
        data = json.loads((folder / ".termina" / f"{name}.json").read_text("utf-8")) \
            if (folder / ".termina" / f"{name}.json").exists() else {}
        self.files = [folder / Path(s["file"].replace("\\", "/")) for s in data.get("slides", [])]
        if not self.files or not all(f.exists() for f in self.files):
            raise RuntimeError(f"Render the slide {name} of the talk {talk} first")
        self.lengths = [self._length(f) for f in self.files]
        self.duration = sum(self.lengths)
        self.colors = colors_of(folder)
        self._open, self._frames, self._last = None, None, None

    @staticmethod
    def _length(f):
        with av.open(str(f)) as c:
            s = c.streams.video[0]
            return float(s.frames / s.average_rate) if s.frames else float(c.duration / av.time_base)

    def frame(self, t):
        """The picture at second t (RGB), decoded forward, so a clip that plays costs little."""
        t = clamp(t, 0, self.duration - 0.04)
        i = 0
        while i < len(self.files) - 1 and t >= self.lengths[i]:
            t -= self.lengths[i]
            i += 1
        if self._open is None or self._open[0] != i or t < self._open[1]:
            self._frames = av.open(str(self.files[i])).decode(video=0)
            self._open, self._last = (i, -1.0), None
        for f in self._frames:
            self._last = f
            if f.time is not None and f.time + 1e-3 >= t:
                break
        self._open = (i, t)
        return self._last.to_ndarray(format="rgb24")

    def still(self, at=0.7):
        return self.frame(self.duration * at).copy()


def colors_of(folder):
    """The colors of a talk, from its style.py: BACKGROUND first."""
    text = (folder / "style.py").read_text("utf-8")
    found = dict(re.findall(r'^(\w+) = "(#[0-9a-fA-F]{6})"', text, flags=re.M))
    keys = ["BACKGROUND"] + [k for k in ("TEXT", "SECONDARY", "ACCENT", "BLUE") if k in found]
    return [found[k] for k in keys]


def _rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], dtype=np.float32)


def recolor(frame, source, target):
    """The frame in other colors. Each pixel is a mix of the background and one color of the
    talk; it becomes the same mix of the new background and the new color."""
    px = frame.astype(np.float32)
    bg, new_bg = _rgb(source[0]), _rgb(target[0])
    fg = np.stack([_rgb(c) for c in source[1:]]) - bg            # k x 3
    new_fg = np.stack([_rgb(c) for c in target[1:]]) - new_bg
    d = px - bg                                                  # h x w x 3
    amount = np.clip(d @ fg.T / np.maximum((fg ** 2).sum(1), 1), 0, 1)  # h x w x k
    miss = ((d[..., None, :] - amount[..., None] * fg) ** 2).sum(-1)
    best = miss.argmin(-1)
    a = np.take_along_axis(amount, best[..., None], -1)
    out = new_bg + a * new_fg[best]
    return np.clip(out, 0, 255).astype(np.uint8)


# The CSS filters that the HTML trailer used, as color matrices.
def hue_rotate(frame, degrees, saturate=1.0):
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    m = np.array([[0.213 + c * 0.787 - s * 0.213, 0.715 - c * 0.715 - s * 0.715, 0.072 - c * 0.072 + s * 0.928],
                  [0.213 - c * 0.213 + s * 0.143, 0.715 + c * 0.285 + s * 0.140, 0.072 - c * 0.072 - s * 0.283],
                  [0.213 - c * 0.213 - s * 0.787, 0.715 - c * 0.715 + s * 0.715, 0.072 + c * 0.928 + s * 0.072]])
    k = saturate
    m2 = np.array([[0.213 + 0.787 * k, 0.715 - 0.715 * k, 0.072 - 0.072 * k],
                   [0.213 - 0.213 * k, 0.715 + 0.285 * k, 0.072 - 0.072 * k],
                   [0.213 - 0.213 * k, 0.715 - 0.715 * k, 0.072 + 0.928 * k]])
    out = frame.astype(np.float32) @ (m2 @ m).T
    return np.clip(out, 0, 255).astype(np.uint8)


class Clip:
    """A slide video in a frame of w x h pixels that plays with the trailer: at second `a` of
    the trailer it shows second `off` of the slide, at the speed `rate`. `look` changes the
    pixels (a theme, a filter)."""

    def __init__(self, slide, w, h, r=0, a=0.0, off=0.0, rate=1.0, circle=False, look=None, zoom=1.0):
        self.mask = None  # a function (width, height) -> alpha from 0 to 1, or None
        self.slide, self.w, self.h, self.r, self.circle = slide, w, h, r, circle
        self.a, self.off, self.rate, self.look, self.zoom = a, off, rate, look, zoom
        self.img = picture(np.zeros((h, w, 3), np.uint8), w, h, r, circle)
        self.el = El(self.img)
        self._shown = None

    def show(self, t, x, y, s=1.0, o=1.0, w=None, h=None, r=None, zoom=None):
        """Puts the frame of second t, centered at (x, y), w x h pixels (by default its own)."""
        w, h = w or self.w, h or self.h
        r = self.r if r is None else r
        rgb = self.slide.frame(self.off + (t - self.a) * self.rate)
        rgba = _rgba(rgb, w * max(s, 0.05), h * max(s, 0.05), r * max(s, 0.05), self.circle, zoom or self.zoom)
        if self.look:  # on the small picture: much faster than on the frame of the film
            rgba[..., :3] = self.look(np.ascontiguousarray(rgba[..., :3]))
        if self.mask:
            rgba[..., 3] = (rgba[..., 3] * self.mask(rgba.shape[1], rgba.shape[0])).astype(np.uint8)
        set_pixels(self.el.base, rgba)
        self.el.base.stretch_to_fit_width(w * U).stretch_to_fit_height(h * U)
        return self.el.at(x, y, s=s, o=o)


def still(slide, w, h, r=0, at=0.7):
    """A picture of a slide (by default at 70 % of its length)."""
    return picture(slide.still(at), w, h, r)




def pill(label, size, weight=500, fg=GRAFITO, bg="#ffffff", edge=NIEBLA, padx=20, pady=8, width=2,
         r=None, icon=None, gap=10):
    """A button like the ones of the app: text (and an icon before it) in a round box. Returns
    an El anchored at its top left, and its width and height in pixels."""
    t = text(label, size, weight, fg)
    iw = icon.width / U + gap if icon is not None else 0
    w, h = t.width / U + iw + 2 * (padx + width), size * 1.276 + 2 * (pady + width)
    b = box(w, h, h / 2 if r is None else r, bg, edge, width if edge else 0)
    left, top = -w / 2 + width + padx, h / 2 - width - pady
    t.move_to([(left + iw) * U + t.width / 2, (top - 0.984 * size) * U - t.baseline, 0])
    parts = [b, t]
    if icon is not None:
        icon.move_to([left * U + icon.width / 2, (top - size * 1.276 / 2) * U, 0])
        parts.append(icon)
    return El(VGroup(*parts), UL), w, h
