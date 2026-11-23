from manim import Cube, FadeIn
from films import play
from films.circle_area import CircleArea


def build(scene):
    play(scene, CircleArea)
    added_1 = Cube(side_length=1.5).move_to((-2.51, -0.56, 0))  # termina
    scene.play(FadeIn(added_1), run_time=0.4)  # termina
