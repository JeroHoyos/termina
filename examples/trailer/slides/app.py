"""28.5-32.5 s: the window of Termina builds itself, the cursor opens the editor, and the camera
dives into the viewer."""

from manim import UL, VGroup

from kit import (ACERO, AZUL, GRAFITO, NIEBLA, U, Clip, El, Slide, View, border, box, cursor, dot,
                 inout, keyframes, lerp, line, out4, p, picture, pill, put, ring, ripple, rise, run,
                 text)
from style import HIELO, OK

APP = (120, 240)  # the top left of the window, 1680 x 800
LIST = [("16", "surface_plots"), ("17", "turing_torus"), ("18", "clifford_torus"),
        ("19", "lorenz_attractor"), ("20", "hopf_fibration"), ("21", "galton_board"), ("22", "times_tables")]


def mark(height):
    """The T of the logo, `height` pixels high, anchored at its top left."""
    k = height / 512
    bar = box(400 * k, 100 * k, 50 * k, GRAFITO).move_to([256 * k * U, -90 * k * U, 0])
    stem = box(100 * k, 295 * k, 50 * k, GRAFITO).move_to([256 * k * U, -187.5 * k * U, 0])
    blue = dot(112 * k, AZUL).move_to([256 * k * U, -422 * k * U, 0])
    return VGroup(bar, stem, blue)


class Parts:
    """Everything of the window, each with its place in the window (x, y) and a group name."""

    def __init__(self):
        self.items = []  # (el, x, y, group)

    def add(self, el, x, y, group="app"):
        self.items.append((el, x, y, group))
        return el

    def row(self, x, y, things, gap, group="bar"):
        """Puts pills in a row from x; returns where it ends."""
        for el, w, h in things:
            self.add(el, x, y - h / 2, group)
            x += w + gap
        return x


def build_bar(parts):
    parts.add(El(box(1680, 84, 22, "#ffffff", NIEBLA, 2), UL), 0, 0, "bar")
    parts.add(El(box(1680, 40, 0, "#ffffff"), UL), 0, 42, "bar")
    parts.add(El(box(1680, 2, 0, NIEBLA), UL), 0, 82, "bar")
    parts.add(El(mark(40), UL), 26 + 3, 22, "bar")
    title = text("Termina", 26, 600)
    parts.add(put(title, 0, 0), 26 + 34 + 20, line(26, 42 - 16.6, 1.276), "bar")
    x = 26 + 34 + 20 + title.width / U + 20 + 16
    x = parts.row(x, 42, [pill("ManimGX examples", 24)], 0) + 10 + 20
    parts.add(El(box(120, 8, 4, NIEBLA), UL), x, 38, "bar")
    parts.add(El(box(120, 8, 4, AZUL), UL), x, 38, "aprog")
    right = [pill("480p", 24), pill("720p", 24, fg="#ffffff", bg=GRAFITO, edge=GRAFITO), pill("1080p", 24),
             pill("Render", 24, fg="#ffffff", bg=AZUL, edge=AZUL), pill("Present", 24), pill("Export", 24)]
    total = sum(w for _, w, _ in right) + 20 * (len(right) - 1)
    parts.row(1680 - 26 - total, 42, right, 20)


def build_list(parts, films):
    parts.add(El(box(400, 676, 16, "#ffffff", NIEBLA, 2), UL), 20, 104, "list")
    for i, (k, name) in enumerate(LIST):
        y = 104 + 10 + i * 92
        group = f"row{i}"
        if name == "hopf_fibration":
            parts.add(El(box(380, 92, 12, HIELO), UL), 30, y, group)
        parts.add(put(text(k, 22, 500, ACERO), 0, 0), 44, line(22, y + 46 - 14, 1.276), group)
        parts.add(El(picture(films[name].still(), 128, 72, 8), UL), 94, y + 10, group)
        parts.add(El(box(128, 72, 8, None, NIEBLA, 1.5), UL), 94, y + 10, group)
        parts.add(put(text(name.replace("_", " ", 1), 22, 500), 0, 0), 238, line(22, y + 18, 1.276), group)
        parts.add(El(dot(12, OK), UL), 238, y + 54, group)
        parts.add(put(text("up to date", 20, 500, ACERO), 0, 0), 258, line(20, y + 47, 1.276), group)


def build_view(parts, films):
    g = "view"
    parts.add(El(box(780, 676, 16, "#ffffff", NIEBLA, 2), UL), 440, 104, g)
    n = text("20", 30, 600, AZUL)
    parts.add(put(n, 0, 0), 464, line(30, 126, 1.276), g)
    name = text("hopf_fibration", 30, 600)
    x = 464 + n.width / U + 14
    parts.add(put(name, 0, 0), x, line(30, 126, 1.276), g)
    parts.add(El(dot(16, OK), UL), x + name.width / U + 20, 137, g)
    parts.add(border(732, 412, 12), 440 + 24 + 366, 104 + 82 + 206, "frame")
    parts.add(El(box(732, 8, 4, NIEBLA), UL), 464, 616, g)
    parts.add(El(box(732, 8, 4, AZUL), UL), 464, 616, "atime")
    edit, w, h = pill("Edit on the slide", 24)
    blue, _, _ = pill("Edit on the slide", 24, fg="#ffffff", bg=AZUL, edge=AZUL)
    parts.add(edit, 464, 652, "edit")
    parts.add(blue, 464, 652, "edited")
    parts.row(464 + w + 14, 652 + h / 2, [pill("Render", 24)], 14, g)
    a, aw, ah = pill("Approve", 24)
    parts.add(a, 464, 716, g)
    parts.row(464 + aw + 14, 716 + ah / 2, [pill("Send to Claude", 24, fg="#ffffff", bg=AZUL, edge=AZUL)], 14, g)


def build_chat(parts):
    g = "chat"
    parts.add(El(box(420, 676, 16, "#ffffff", NIEBLA, 2), UL), 1240, 104, g)
    q = text("What should we change?", 34, 600)
    buttons = [pill(s, 24) for s in ("Improve this slide", "Apply my notes", "Add a slide after")]
    h = 34 * 1.276 + 10 + sum(b[2] + 18 for b in buttons)
    y = 104 + (676 - h) / 2
    parts.add(put(q, 0, 0), 1450 - q.width / U / 2, line(34, y, 1.276), g)
    y += 34 * 1.276 + 10 + 18
    for el, w, bh in buttons:
        parts.add(el, 1450 - w / 2, y, g)
        y += bh + 18


class Window:
    def __init__(self):
        films = {n: Slide("manimgx-examples", n) for _, n in LIST}
        self.film = Clip(films["hopf_fibration"], 732, 412, 12, a=28.5, off=12)
        self.parts = Parts()
        self.parts.add(El(box(1680, 800, 22, "#f6f6f3", NIEBLA, 2), UL), 0, 0, "app")
        build_bar(self.parts)
        build_list(self.parts, films)
        build_view(self.parts, films)
        build_chat(self.parts)
        # the film is drawn over its panel and under its frame line
        self.mobjects = []
        for el, *_, g in self.parts.items:
            if g == "frame":
                self.mobjects.append(self.film.el.m)
            self.mobjects.append(el.m)

    def group(self, t, g):
        """Move, scale and opacity of a group of the window at time t."""
        if g in ("view", "frame", "atime", "edit", "edited"):
            vs = out4(p(t, 29.2, 29.8))
            return 0, lerp(0.9, 1, vs), vs
        if g == "list" or g.startswith("row"):
            o = p(t, 29.3 + int(g[3:]) * 0.06, 29.6 + int(g[3:]) * 0.06) if g.startswith("row") else 1
            return (1 - out4(p(t, 29.0, 29.6))) * -460, 1, o
        if g == "chat":
            return (1 - out4(p(t, 29.1, 29.7))) * 480, 1, 1
        return 0, 1, p(t, 28.9, 29.2) if g in ("bar", "aprog") else 1

    def frame(self, t):
        up = out4(p(t, 28.6, 29.4))
        z = inout(p(t, 31.2, 32.5))
        zoom = lerp(1, 2.4, z)
        vx, vy = 120 + 440 + 24 + 366, 240 + 104 + 82 + 206
        cam = View(dx=lerp(0, 960 - vx * zoom, z), dy=lerp(0, 575 - vy * zoom, z), s=zoom, cx=0, cy=0,
                   o=up * (1 - p(t, 32.2, 32.5)))
        ax, ay = APP[0], APP[1] + (1 - up) * 500
        for el, x, y, g in self.parts.items:
            self.place(t, cam, el, ax + x, ay + y, g, (ax + 830, ay + 442))
        _, s, o = self.group(t, "view")
        cam.show(self.film, t, ax + 830, ay + 442 + (392 - 442) * s, s=s, o=o)

    def place(self, t, cam, el, x, y, g, center):
        dx, s, o = self.group(t, g)
        if s != 1:  # the viewer grows around the center of its panel
            x, y = center[0] + (x - center[0]) * s, center[1] + (y - center[1]) * s
        sx = 1.0
        if g == "aprog":
            sx = (60 + 40 * p(t, 29.6, 30.6)) / 100
        if g == "atime":
            sx = (40 + 30 * p(t, 29.2, 32.5)) / 100
        if g in ("edit", "edited"):
            o *= (t <= 30.75) if g == "edit" else (t > 30.75)
        cam.at(el, x + dx, y, s=s, o=o, sx=sx)


def build(scene):
    window = Window()
    title = put(text("Meet Termina", 140, spacing=-0.045), 960, line(140, 56), "center")
    arrow, rip = cursor(), ring()
    keys = [(29.6, 1500, 1100), (30.6, 700, 905), (31.0, 700, 905)]

    def frame(t):
        rise(title, t, 28.55, 960, line(140, 56), 140, 31.2, 0.7)
        window.frame(t)
        x, y = keyframes(t, keys)
        down = 30.75 < t < 30.93
        arrow.at(x, y, s=0.85 if down else 1, o=p(t, 29.6, 29.8) * (1 - p(t, 31.4, 31.6)))
        ripple(rip, t, 30.75, x + 8, y + 6)

    run(scene, 28.5, 32.5, frame, title.m, *window.mobjects, arrow.m, rip.m)
