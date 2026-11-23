from films import play
from films.lorenz_attractor import LorenzAttractor


def build(scene):
    play(scene, LorenzAttractor)
