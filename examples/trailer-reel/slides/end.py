"""68.5-76 s: the end. The name, what Termina is, where to get it, and that this reel is made
with Termina; then the screen fades."""

from kit import ACERO, NIEBLA, El, back, box, clamp, lerp, line, out4, p, pill, put, rise, run, text
from style import AZUL, GRAFITO, HUESO
from trailer.end import wordmark

TOP = 560  # the top of the wordmark, 840 x 248 pixels
LINES = ["Talks made with math,", "one slide at a time"]


def build(scene):
    mark = wordmark()
    tagline = [put(text(s, 64, 400, ACERO, -0.015), 540, line(64, 900 + i * 76, 1.1), "center")
               for i, s in enumerate(LINES)]
    link = put(text("github.com/JeroHoyos/termina", 34, 500, GRAFITO, 0.06, mono=True), 540,
               line(34, 1110, 1.276), "center")
    small = put(text("OPEN SOURCE   MIT   WINDOWS AND LINUX", 26, 500, ACERO, 0.14, mono=True), 540,
                line(26, 1180, 1.276), "center")
    made, made_w, made_h = pill("This reel was made with Termina", 32, 500, GRAFITO, "#ffffff", NIEBLA, 26, 12,
                                icon=box(18, 18, 9, AZUL), gap=14)
    curtain = El(box(1080, 1920, 0, HUESO))

    def frame(t):
        e = out4(p(t, 68.5, 69.2))
        s = lerp(0.9, 1, e)
        mark.at(120 + 420 * (1 - s), TOP + 111 * (1 - s), s=s, o=e)
        for i, el in enumerate(tagline):
            rise(el, t, 69.2 + i * 0.1, 540, line(64, 900 + i * 76, 1.1), 64, d=0.8)
        link.at(540, line(34, 1110, 1.276), o=p(t, 69.9, 70.5))
        small.at(540, line(26, 1180, 1.276), o=p(t, 70.3, 70.9))
        e = back(p(t, 71.2, 71.6))
        made.at(540 - made_w / 2 * e, 1290 + made_h / 2 * (1 - e), s=max(e, 0.001), o=clamp(e))
        curtain.at(540, 960, o=p(t, 74.6, 75.8))

    run(scene, 68.5, 76, frame, mark.m, *[el.m for el in tagline], link.m, small.m, made.m, curtain.m)
