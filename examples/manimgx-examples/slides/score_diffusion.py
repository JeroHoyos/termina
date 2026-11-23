from films import play
from films.score_diffusion import ScoreDiffusion


def build(scene):
    play(scene, ScoreDiffusion)
