from manim import BOLD, DOWN, UP, Circle, Create, FadeIn, Square, Text, Transform, config

from style import ACCENT, FONT, TEXT, TITLE_SIZE

TITLE = "Slide title"


def build(scene):
    title = Text(TITLE, font=FONT, font_size=TITLE_SIZE, color=TEXT, weight=BOLD)
    if title.width > config.frame_width - 1.5:
        title.scale_to_fit_width(config.frame_width - 1.5)
    title.to_edge(UP, buff=0.8)
    shape = Square(side_length=2.5, color=ACCENT)

    scene.play(FadeIn(title, shift=DOWN * 0.2), run_time=0.7)
    scene.play(Create(shape), run_time=1)
    scene.play(Transform(shape, Circle(radius=1.4, color=ACCENT)), run_time=1)
    scene.wait(1)
