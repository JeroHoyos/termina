---
name: manim-math
description: How to make good mathematical animations and 3D models in the slides of a Termina talk (Manim Community + manim-slides). Use it together with the `slides` skill when a slide has formulas, graphs, axes, vectors, geometry, a transformation, a simulation, a surface, a solid or any 3D model, or when the user asks for a slide "like 3Blue1Brown".
---

# Mathematical animations and 3D models

This skill says *how to draw* the content. The `slides` skill says how to create, render and
review a slide: follow it for the flow. The talks use Manim Community 0.18–0.21 with `Slide` (2D).

## Before you write

1. Put the mathematics in a helper file next to `main.py` (as `lorenz.py` and `epicycles.py` in
   `termina/examples/`). It uses only numpy and gives points, values or functions. The slide file
   only tells the story. Run the helper with a short `python -c` and look at the numbers before
   you render: a wrong sign costs a full render.
2. Formulas: `MathTex` needs LaTeX. Run `latex --version` once. If there is no LaTeX, use `Text`
   with Unicode (x², √, π, ∑, ∫, →) and check that the talk's `FONT` has the symbols, or ask the
   user to install LaTeX (MiKTeX on Windows, `texlive` on Linux).
3. Use the colors and sizes of the talk's `style.py`. Give each mathematical object one color and
   keep it in all the slide: the same `x` is always the same color in the formula, on the axis and
   in the graph.

## Patterns that work

**One tracker moves everything.** A `ValueTracker` for the time or the parameter, and each part
reads it with `always_redraw(lambda: ...)` or `add_updater`. The parts stay in step, and one
`play(t.animate.set_value(...))` moves all of them.

```python
t = ValueTracker(0)
dot = always_redraw(lambda: Dot(axes.c2p(t.get_value(), f(t.get_value())), color=ACCENT))
value = always_redraw(lambda: DecimalNumber(f(t.get_value()), num_decimal_places=2).next_to(dot, UP))
scene.play(t.animate.set_value(3), run_time=4, rate_func=smooth)
```

**Graphs.** `axes = Axes(x_range=[-3, 3, 1], y_range=[-1, 4, 1], x_length=8, y_length=5)`,
`axes.plot(f, color=...)`, `axes.get_graph_label(graph, "f(x)")`, `axes.c2p(x, y)` for a point.
Draw the axes first, then `Create(graph)`. For an area: `axes.get_area(graph, x_range=(a, b))`;
for Riemann sums: `axes.get_riemann_rectangles(graph, dx=...)` and make `dx` smaller in steps.

**Equations that change.** Isolate the parts that move:
`MathTex("a^2", "+", "b^2", "=", "c^2")` or `substrings_to_isolate=["x", "y"]`, color them with
`set_color_by_tex`, and go from one step to the next with `TransformMatchingTex(old, new)`. The
eye follows each part. Without LaTeX, `TransformMatchingShapes` does the same with `Text`.

**Linear algebra and changes of coordinates.** `NumberPlane()` and
`ApplyMatrix([[a, b], [c, d]], plane)`; put the basis vectors (`Arrow` or `Vector`) in the same
`ApplyMatrix`. For a function that is not linear: `plane.prepare_for_nonlinear_transform()` and
then `plane.animate.apply_function(f)`.

**Paths and simulations.** Calculate the points in the helper (Runge–Kutta, as in `lorenz.py`),
and show them with `VMobject().set_points_as_corners(points[:n])` in an updater. `TracedPath`
draws the trail of a point that moves. A `VMobject` needs at least two points.

**Fields.** `ArrowVectorField(f)` for the arrows and `StreamLines(f)` with
`start_animation(warm_up=False)` for the flow.

**Attention.** `Indicate`, `Circumscribe` and `Flash` point to a part. `LaggedStart(*anims,
lag_ratio=0.15)` shows a group one by one. Fade the rest to `opacity=0.3` instead of removing it.

**Pauses.** One `scene.next_slide()` after each step of the idea. A slide that moves while the
speaker talks ends with `next_slide(loop=True)`, an animation that ends where it starts (a full
turn, `TAU`), and `next_slide()`.

## 3D models

### Default: 3D in a 2D slide with `view3d.py`

Copy `view3d.py` (in the folder of this skill) next to the talk's `main.py`. The slide stays a 2D
slide: the fade between slides, the text, the page number and the editor of the app work.

```python
from view3d import CUBE, curve, graph, solid, surface

yaw = ValueTracker(-0.6)
hill = always_redraw(lambda: graph(
    lambda x, y: np.exp(-(x * x + y * y)), (-2, 2), (-2, 2),
    yaw=yaw.get_value(), pitch=0.5, scale=1.2, center=(0, -0.5), color=(BLUE, ACCENT)))
axis = curve([(0, 0, 0), (0, 0, 2)], yaw=-0.6, pitch=0.5, scale=1.2, color=TEXT)
scene.add(hill)
scene.play(yaw.animate.increment_value(TAU), run_time=10, rate_func=linear)
```

- `view` and `project` turn 3D points into the frame of the camera or the screen. `yaw` turns
  around the vertical axis, `pitch` looks from above, `distance` adds perspective.
- `solid(vertices, faces)` draws any model of flat faces with light (`CUBE` is an example).
  `surface(f, u_range, v_range)` is a parametric surface (sphere, torus, Möbius strip), and
  `graph(f)` is `z = f(x, y)`. `color` is one color or a pair (low, high) by height.
- Faces are sorted from the back to the front. Two surfaces that cut each other are not drawn
  correctly: make them one `solid` with all the faces.
- The cost goes with the faces: a grid of 24×24 is good. More than 40×40 makes the render slow.
  Use the same `yaw`, `pitch`, `scale` and `center` for all the parts of one scene.

### Real 3D with `ThreeDSlide`

Use it only if `view3d.py` is not enough (surfaces that cut, a camera that flies) and the user
agrees, because it changes the full talk:

- the class in `main.py` changes from `Slide` to `ThreeDSlide`;
- the camera stays as the last slide left it: the talk's `start_slide` must reset it with
  `self.set_camera_orientation(phi=0, theta=-90 * DEGREES)` and stop
  `self.stop_ambient_camera_rotation()`;
- each `Text` and formula must be fixed with `scene.add_fixed_in_frame_mobjects(m)`, or it turns
  with the scene;
- the boxes of the editor of the app are wrong for objects in 3D, and the render is much slower.

## Review the result

Look at the stills (the `slides` skill) and check:

- The mathematics is correct: axes with their labels, signs, values and units.
- Nothing goes out of the frame (14.2 × 8 units) and no text is on top of a graph or a model.
- A 3D model reads well: the light shows its form, and the angle shows all the parts that matter.
- A loop ends where it starts, so the jump is not visible.
- For a slow render (3D, many objects), make a draft with `--quality 480p` first, then the
  talk's resolution.
