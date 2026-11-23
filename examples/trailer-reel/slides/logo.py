"""0-4.5 s: the logo of the trailer, larger and in the middle of the reel."""

from trailer import logo as base

K = 900 / 1770  # the logo is 900 pixels wide
LEFT = 540 - 256 * K  # the T starts in the middle; the whole logo ends in the middle (its center is x = 906 of the SVG)


def build(scene):
    base.build(scene, base.Logo(K, LEFT, 960 - 260 * K - 40, 540 - 906 * K - LEFT))
