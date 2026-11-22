---
name: manim-math
description: How to make good mathematical animations and 3D models in the slides and scenes of a Termina talk or video (Manim Community + manim-slides), in the style of 3Blue1Brown. Use it together with the `slides` skill when a slide has formulas, graphs, axes, vectors, geometry, a transformation, a simulation, a probability distribution, a surface, a solid or any 3D model, or when the user asks for a slide or a video "like 3Blue1Brown".
---

# Mathematical animations and 3D models

This skill says *how to draw* the content. The `slides` skill says how to create, render and
review a slide: follow it for the flow. The talks use Manim Community 0.18–0.21 with `Slide` (2D).

The rules here come from 15 ports of 3Blue1Brown videos to Manim CE (the `3b1b/` folder next to
`termina/`, if it is there). `examples.md` in the folder of this skill gives the technique of
each port. Before you start a topic that is near one of them, read its recipe, and if the folder
is there, read its `diapositivas/escena.py`: about 100 lines that work.

## The 3Blue1Brown way

1. **One question, then the answer.** Each scene is one idea. The first caption shows the object
   ("A signal that beats 3 times per second"). The middle captions say what to do or what to look
   at ("Wind it around a point"). The last caption is the conclusion ("The peak gives the
   frequency"). Then `scene.wait(2)` or `scene.wait(3)`, so the audience reads it.
2. **A caption is a sentence, not a label.** One line at the top, in the talk's `TEXT_SIZE`.
   Change it with `Transform(caption, _caption("…"))` in the same `play` as the motion that it
   explains, so the words and the picture change together.
3. **Show it before you name it.** Let the audience see the pattern (the spirals, the bell, the
   whirl at the pole), then show the formula or the name. The formula comes last, in the color of
   the object that it describes.
4. **Choose numbers that make the story clear.** A loaded die with a clear asymmetry, masses
   1 kg and 100 kg (31 collisions), a matrix with integer entries, a signal at 3 Hz. Scale the
   physics so the times are round: in `braquistocrona` gravity is set so the ball takes 2 s.
5. **Start slow, then go fast.** The first steps of a repeated process are slow, so the eye
   learns the rule. Then the rest go fast (`binario`: 0.7 s for 1–8, 0.3 s for 9–31).
6. **One color for each concept, in all the scene.** 3Blue1Brown uses: î green, ĵ red, a vector
   or the thing that is important `YELLOW`, a second quantity `BLUE` or the talk's `ACCENT`,
   context `SECONDARY` or `GREY_B`, a problem point (a zero, a whirl) `RED`.
7. **Keep the context.** Do not remove an object that the next step needs. Fade it to
   `opacity=0.15`–`0.3` and put the new thing on top (`choques`: the blocks fade, the table
   comes up). Keep a faint copy of the grid behind a grid that moves (`transformaciones`).
8. **The camera does not stop.** In 3D, each beat also turns the model a little
   (`yaw.animate.increment_value(0.4)` in the same `play`). A model that stands still looks flat.
9. **End on the conclusion.** The scene ends on the last caption and the result, not on a fade
   to black. The talk's `end` slide does the fade.

## Before you write

1. Put the mathematics in a helper file next to `main.py` (as `lorenz.py` and `epicycles.py` in
   `termina/examples/`), or at the top of the slide file if it is short (as in the `3b1b/` ports).
   It uses only numpy and gives points, values or functions. `build(scene)` only tells the story.
   Run the helper with a short `uv run python -c "…"` and look at the numbers before you render:
   a wrong sign costs a full render.
2. Calculate each number that a caption or a table shows, and check it with the helper
   (`braquistocrona` shows "2,37 s": that is `2·√(π²+4)/π`). Never write a number that you did
   not calculate.
3. Formulas: `MathTex` needs LaTeX. Run `latex --version` once. If there is no LaTeX, use `Text`
   with Unicode (x², √, π, ∑, ∫, →, î, ĵ) and check that the talk's `FONT` has the symbols, or ask
   the user to install LaTeX (MiKTeX on Windows, `texlive` on Linux).
4. Use the colors and sizes of the talk's `style.py`. Give each mathematical object one color and
   keep it in all the slide: the same `x` is always the same color in the formula, on the axis and
   in the graph.

## The shape of a scene

All the ports have this shape. Use it as the start of a new scene:

```python
def _caption(text):
    return Text(text, font=FONT, font_size=TEXT_SIZE, color=TEXT).to_edge(UP, buff=0.35)


def build(scene):
    t = ValueTracker(0)                                    # the one parameter of the scene
    model = always_redraw(lambda: _model(t.get_value()))   # everything that depends on it
    caption = _caption("What we look at")
    scene.play(FadeIn(caption), FadeIn(model))
    scene.wait(1)
    scene.play(Transform(caption, _caption("What to do")), t.animate.set_value(1), run_time=4)
    scene.play(Transform(caption, _caption("What it means")))
    scene.wait(3)
```

- Small functions with a `_` (`_model`, `_arrows`, `_caption`) make one object from the values.
  `build` only holds the trackers and the order of the beats.
- In a slide (not a video), put `scene.next_slide()` after each beat. In a video the `_slide`
  wrapper makes the cut: do not call it.
- `_caption` keeps the text in the frame: if a caption is too wide, make it shorter. Do not make
  the font smaller.

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

- Use `rate_func=linear` when the tracker is time or an angle that turns. `smooth` (the default)
  is for a move from one state to a different state.
- A tracker can mix two states: `field = (1 - mix) * spin + mix * flow` and animate `mix` from 0
  to 1 (`bola-peluda`). A tracker can also be an opacity: `.set_opacity(red.get_value())` shows a
  part slowly while the rest moves.
- An `always_redraw` can read a Python list. Append to the list between two `play` calls and the
  next frame shows the new item (`palabras-vectores`: `shown.append("reina")`).

**Two views, one tracker.** Put the geometry on the left and a graph of a number from it on the
right, both driven by the same tracker (`fourier`: the wound signal and its center of mass;
`epidemia`: the people and the stacked areas). The graph draws only up to the value of the
tracker, so it grows as the parameter moves:

```python
curve = always_redraw(lambda: axes.plot(g, x_range=[a, max(f.get_value(), a + 0.02), 0.01], color=RED))
```

`x_range` must not be empty: that is why there is `max(..., a + 0.02)`.

**A process in steps.** Make the object of step `n` with a function, and go from one step to the
next with `Transform(obj, _make(n))` in a loop (`hilbert`: orders 1 to 7; `limite-central`: the
sum of 1 to 30 dice; `binario`: 0 to 31). Put a small label "order n" in a corner and transform it
too.

**Morph between two layouts.** Give the two layouts the same objects in the same order, and each
polygon its vertices in the same order (`pitagoras`: each triangle is the right angle, the end of
leg a, the end of leg b). Then `Transform(group_a, group_b)` moves each piece to its new place
without twists.

**Graphs.** `axes = Axes(x_range=[-3, 3, 1], y_range=[-1, 4, 1], x_length=8, y_length=5)`,
`axes.plot(f, color=...)`, `axes.get_graph_label(graph, "f(x)")`, `axes.c2p(x, y)` for a point.
Draw the axes first, then `Create(graph)`. For an area: `axes.get_area(graph, x_range=(a, b))`;
for Riemann sums: `axes.get_riemann_rectangles(graph, dx=...)` and make `dx` smaller in steps.
Give the axes `axis_config={"color": SECONDARY}`, so the data is brighter than the axes.

**Equations that change.** Isolate the parts that move:
`MathTex("a^2", "+", "b^2", "=", "c^2")` or `substrings_to_isolate=["x", "y"]`, color them with
`set_color_by_tex`, and go from one step to the next with `TransformMatchingTex(old, new)`. The
eye follows each part. Without LaTeX, `TransformMatchingShapes` does the same with `Text`.

**Text on a grid or a picture.** Give the text a background:
`MathTex(...).add_background_rectangle(color=BACKGROUND, opacity=0.85, buff=0.15)`. Without it,
the lines of the grid go through the letters.

**Linear algebra and changes of coordinates.** Put a faint `NumberPlane` that does not move
behind a bright `NumberPlane` that moves (make the bright one 2× larger, so its edges do not come
into the frame after the matrix). Then `plane.animate.apply_matrix(M)` and, in the same `play`,
`Transform(vectors, _vectors(M @ i, M @ j, M @ v))`. Calculate the new ends with numpy. For a
function that is not linear: `plane.prepare_for_nonlinear_transform()` and then
`plane.animate.apply_function(f)`.

**Paths and simulations.** Calculate the points in the helper (Runge–Kutta, as in `lorenz.py`),
and show them with `VMobject().set_points_as_corners(points[:n])` in an updater. `TracedPath`
draws the trail of a point that moves (`braquistocrona`: the point on the wheel; `paralaje`: the
star on the far wall). A `VMobject` needs at least two points.

**Fields.** `ArrowVectorField(f)` for the arrows and `StreamLines(f)` with
`start_animation(warm_up=False)` for the flow.

**Many points.** To 2000 points, use `Dot` in a `VGroup`. For more (`espirales`: the primes to
250 000), use one `PMobject` with `add_points(points, color=...)`: it is fast. To zoom out to a
larger scale, shrink the old points to nothing and grow the new ones in the same `play`:
`old.animate.scale(0.004, about_point=c).set_opacity(0)`, `FadeIn(new, scale=3)`. Then
`scene.remove(old)`.

**A line that shows direction.** `set_stroke(color=[BLUE, TEAL, GREEN, YELLOW])` paints a
gradient from the start to the end of a path, so the eye sees the order (`hilbert`). Make the
stroke thinner when the path has more corners.

**Attention.** `Indicate`, `Circumscribe` and `Flash` point to a part. `LaggedStart(*anims,
lag_ratio=0.15)` or `FadeIn(group, lag_ratio=0.3)` shows a group one by one. Fade the rest to
`opacity=0.3` instead of removing it.

**Pauses.** One `scene.next_slide()` after each step of the idea. A slide that moves while the
speaker talks ends with `next_slide(loop=True)`, an animation that ends where it starts (a full
turn, `TAU`), and `next_slide()`.

## Simulations, probability and data

- **Calculate all of it first.** Run the simulation once, when the module loads, into numpy
  arrays (`POSITIONS[step, person]`, `STATES[step, person]`). The updater only reads the row:
  `i = int(step.get_value())`. Use a fixed seed (`np.random.default_rng(3)`), so each render is
  the same. Try seeds with the helper and keep one that tells the story well.
- **Exact events, not small time steps.** For collisions and bounces, calculate the time of the
  next event, jump to it, and save `(time, positions, velocities, count)` (`choques`). Between two
  events the motion is linear: `state(t)` finds the last event with `bisect_right` and moves from
  it. This is exact, also when there are 3141 collisions.
- **Simulation time = video time.** Animate the time tracker with `run_time=end` and
  `rate_func=linear`, so one second of the simulation is one second of the video.
- **Exact distributions.** For the sum of dice, convolve the probabilities (`np.convolve`) in
  place of random samples: the bars do not shake. To compare shapes, move and scale each one to
  mean 0 and deviation 1, and draw each bar with an area equal to its probability.
- **Stacked areas.** One `Polygon` for each band: the top edge from left to right, then the bottom
  edge from right to left (`epidemia`).
- **Stop the updaters before you change the objects.** Before a fade or a `.animate` on objects
  with updaters, call `m.clear_updaters()` on each one (`choques`), or the updater puts them back
  on each frame.

## 3D models

### Default: 3D in a 2D slide with `view3d.py`

Copy `view3d.py` (in the folder of this skill) next to the talk's `main.py`. The slide stays a 2D
slide: the fade between slides, the text, the page number and the editor of the app work. Five
of the `3b1b/` ports use it (`bola-peluda`, `esfera`, `paralaje`, `palabras-vectores`,
`rectangulo-inscrito`).

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

Idioms from the ports:

- **One projection for the scene.** Put `PITCH, SCALE, CENTER` (and `DISTANCE`) in constants
  and write `def _p(points, yaw): return project(points, yaw, PITCH, SCALE, CENTER)`. Then all
  the parts agree.
- **The camera turns, the model does not change.** `yaw` is the only `ValueTracker` of the
  camera. Each `always_redraw` reads it. To turn and change at the same time, put the two in one
  `play`.
- **Hide what is behind.** `solid` sorts its faces, but dots and arrows on a model do not. Draw
  only the ones on the front: `front = view(points, yaw, PITCH)[:, 2] < 0` (z goes away from the
  camera), then skip the others (`bola-peluda`: the arrows and the poles on the sphere). Put
  points a little above the surface (`points * 1.01`) so they are not inside it.
- **Arrows in 3D.** Project the start and the end, then make a 2D
  `Arrow(s, e, buff=0, tip_length=0.1, max_tip_length_to_length_ratio=0.4)`. Skip the arrows
  that are shorter than 0.04 on the screen: they are only a tip.
- **Points that cover a sphere.** Use the Fibonacci sphere: `z = 1 - 2(i + 0.5)/n`,
  angle `π(1 + √5)·i`. A grid of latitude and longitude puts too many points at the poles.
- **Open the model.** Move the parts of a solid away from each other with a tracker
  (`esfera`: each band of latitude goes up or down by `spread · (b - middle)`), then close it.
- **A space with labels.** Draw the axes with `curve` from the origin, the words with `Text` at
  `_p(point)` and `next_to(..., buff=0.05)`. The text stays flat and readable while the space turns
  (`palabras-vectores`).
- **Perspective for depth.** Give `distance` (about 14) when the scene is deep, as a solar system
  with stars far away (`paralaje`). For one object, no `distance` is clearer.

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

- The mathematics is correct: axes with their labels, signs, values and units. Each number in a
  caption agrees with the helper.
- Each caption is one line, inside the frame, and does not cover the model.
- Nothing goes out of the frame (14.2 × 8 units) and no text is on top of a graph or a model.
- A 3D model reads well: the light shows its form, and the angle shows all the parts that matter.
  No dot or arrow from the back shows through.
- The last frame shows the conclusion and stays long enough to read it.
- A loop ends where it starts, so the jump is not visible.
- For a slow render (3D, many objects, simulations), make a draft with `--quality 480p` first,
  then the talk's resolution.
