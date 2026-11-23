"""28.5-32.5 s: the window of Termina builds itself, the cursor opens the editor, and the camera
dives into the viewer. The window of the trailer, at 60 %."""

from kit import View, cursor, keyframes, line, p, placed, put, ring, ripple, rise, run, text
from trailer.app import Window

WINDOW = View(dx=540 - 960, dy=1020 - 640, s=0.6, cx=960, cy=640)


def build(scene):
    window = Window()
    title = put(text("Meet Termina", 150, spacing=-0.045), 540, line(150, 520), "center")
    arrow, rip = cursor(), ring()
    keys = [(29.6, 1500, 1100), (30.6, 700, 905), (31.0, 700, 905)]

    def frame(t):
        rise(title, t, 28.55, 540, line(150, 520), 150, 31.2, 0.7)
        with placed(WINDOW):
            window.frame(t)
        x, y = WINDOW.xy(*keyframes(t, keys))
        down = 30.75 < t < 30.93
        arrow.at(x, y, s=0.85 if down else 1, o=p(t, 29.6, 29.8) * (1 - p(t, 31.4, 31.6)))
        ripple(rip, t, 30.75, x + 8, y + 6)

    run(scene, 28.5, 32.5, frame, title.m, *window.mobjects, arrow.m, rip.m)
