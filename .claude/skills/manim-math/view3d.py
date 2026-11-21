"""3D models in a 2D slide: points seen by a camera, and faces drawn from the back to the front.

Copy this file next to the talk's main.py. The slides stay normal 2D slides, so the fade between
slides, the text and the editor of the app work as before.

The camera turns around the vertical axis (`yaw`) and looks down from above (`pitch`), both in
radians. z is up. Put a ValueTracker in `yaw` and redraw with `always_redraw` to turn a model.
"""

import numpy as np
from manim import WHITE, ManimColor, Polygon, VGroup, VMobject, interpolate_color


def view(points, yaw=-0.6, pitch=0.5):
    """The points in the frame of the camera: x to the right, y up, z away from the camera."""
    p = np.asarray(points, dtype=float).reshape(-1, 3)
    cy, sy, cp, sp = np.cos(yaw), np.sin(yaw), np.cos(pitch), np.sin(pitch)
    x = p[:, 0] * cy - p[:, 1] * sy
    d = p[:, 0] * sy + p[:, 1] * cy
    return np.column_stack([x, p[:, 2] * cp + d * sp, d * cp - p[:, 2] * sp])


def project(points, yaw=-0.6, pitch=0.5, scale=1.0, center=(0.0, 0.0), distance=None):
    """The points as the screen shows them. With `distance`, far parts are smaller (perspective)."""
    v = view(points, yaw, pitch)
    k = scale if distance is None else scale * distance / (distance + v[:, 2])
    k = np.broadcast_to(k, len(v))
    return np.column_stack([v[:, 0] * k + center[0], v[:, 1] * k + center[1], np.zeros(len(v))])


def curve(points, yaw=-0.6, pitch=0.5, scale=1.0, center=(0.0, 0.0), distance=None, **style):
    """A line through 3D points: a path, an axis, the edge of a model."""
    line = VMobject(**style)
    line.set_points_as_corners(project(points, yaw, pitch, scale, center, distance))
    return line


def solid(vertices, faces, yaw=-0.6, pitch=0.5, scale=1.0, center=(0.0, 0.0), distance=None,
          color=WHITE, opacity=1.0, stroke=0.5, light=(-0.4, 0.6, -0.7), dark=0.35):
    """A model made of flat faces, with light on the faces that look to it.

    `faces` are lists of indexes into `vertices`. `color` is one color, or a pair (low, high) that
    goes from the lowest face to the highest one. `dark` is the light of a face in the shadow.
    """
    vertices = np.asarray(vertices, dtype=float)
    seen = view(vertices, yaw, pitch)
    screen = project(vertices, yaw, pitch, scale, center, distance)
    light = np.asarray(light, dtype=float) / np.linalg.norm(light)
    pair = isinstance(color, (tuple, list))
    heights = [vertices[f, 2].mean() for f in faces]
    low, high = min(heights), max(heights)
    order = sorted(range(len(faces)), key=lambda i: -seen[faces[i], 2].mean())
    group = VGroup()
    for i in order:
        f = faces[i]
        a, b, c = seen[f[0]], seen[f[1]], seen[f[-1]]
        normal = np.cross(b - a, c - a)
        size = np.linalg.norm(normal)
        shade = dark + (1 - dark) * (abs(normal @ light) / size if size else 0)
        if pair:
            base = interpolate_color(ManimColor(color[0]), ManimColor(color[1]),
                                     (heights[i] - low) / (high - low) if high > low else 0)
        else:
            base = ManimColor(color)
        fill = interpolate_color(ManimColor("#000000"), base, shade)
        group.add(Polygon(*screen[f], fill_color=fill, fill_opacity=opacity, stroke_color=fill,
                          stroke_width=stroke))
    return group


def surface(f, u_range=(-1, 1), v_range=(-1, 1), resolution=(24, 24), **options):
    """The surface of f(u, v) -> (x, y, z), as a grid of faces. The options are those of solid."""
    nu, nv = resolution
    us, vs = np.linspace(*u_range, nu + 1), np.linspace(*v_range, nv + 1)
    vertices = [f(u, v) for u in us for v in vs]
    faces = [[i * (nv + 1) + j, (i + 1) * (nv + 1) + j, (i + 1) * (nv + 1) + j + 1,
              i * (nv + 1) + j + 1] for i in range(nu) for j in range(nv)]
    return solid(vertices, faces, **options)


def graph(f, x_range=(-1, 1), y_range=(-1, 1), resolution=(24, 24), **options):
    """The surface z = f(x, y)."""
    return surface(lambda x, y: (x, y, f(x, y)), x_range, y_range, resolution, **options)


CUBE = (
    [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)],
    [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]],
)
