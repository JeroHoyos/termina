"""46.5-52.5 s: Claude fixes it. The slide is on top; the chat and the button are under it."""

from kit import View, cursor, keyframes, line, p, placed, put, rise, run, text
from trailer.claude import Approve, Chat, Fix

FIX = View(dx=540 - 660, dy=760 - 574, s=0.92, cx=660, cy=574)       # the slide, 994 pixels wide
CHAT = View(dx=300 - 1530, dy=1350 - 574, s=0.8, cx=1530, cy=574)    # the chat, on the left
BUTTON = View(dx=790 - 1407, dy=1350 - 957, cx=1407, cy=957)          # the button, on the right


def build(scene):
    title = put(text("Claude fixes it", 130, spacing=-0.04), 540, line(130, 290), "center")
    fix, chat, approve = Fix(), Chat(), Approve()
    arrow = cursor()
    keys = [(50.4, 1700, 1100), (51.1, 1340, 945), (51.6, 1340, 945)]

    def frame(t):
        rise(title, t, 46.6, 540, line(130, 290), 130, 52.0)
        with placed(FIX):
            fix.frame(t)
        with placed(CHAT):
            chat.frame(t)
        with placed(BUTTON):
            approve.frame(t)
        x, y = BUTTON.xy(*keyframes(t, keys))
        arrow.at(x, y, s=0.85 if 51.2 < t < 51.38 else 1, o=p(t, 50.4, 50.6) * (1 - p(t, 51.8, 52.0)))

    run(scene, 46.5, 52.5, frame, title.m, *fix.mobjects, *chat.mobjects, *approve.mobjects, arrow.m)
