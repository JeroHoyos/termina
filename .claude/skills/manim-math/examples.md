# The 3Blue1Brown ports: one recipe for each

These are 15 videos of Termina (`"kind": "video"`) in the `3b1b/` folder next to `termina/`. Each
one is a port to Manim Community of a scene from the code of 3Blue1Brown (the `_20xx/...` path).
Each one has one scene, `diapositivas/escena.py`, of 100 to 200 lines. They all have the same
`style.py` (dark background `#0c0c0f`, `ACCENT` `#58c4dd`) and the same `view3d.py` as this skill.

To make a new scene on a near topic, read the port first and copy its structure, not its text.

| Port | Original | Idea | Technique to copy |
| --- | --- | --- | --- |
| `binario` | `_2015/counting_in_binary.py` | Count to 31 with 5 bits | Loop of `Transform` on each digit; box fill = bit; slow first steps, then fast |
| `pitagoras` | `_2015/pythagorean_proof.py` | Proof by rearrangement | Two lists of triangle corners in the same order; one `Transform` between them |
| `hilbert` | `_2016/hilbert/section1.py` | A curve fills the square | `Transform` from order n to n+1; gradient stroke; thinner stroke at higher order |
| `braquistocrona` | `_2016/brachistochrone/cycloid.py` | Cycloid, and the race | Rolling wheel with `TracedPath`; physics scaled to round times; exact times in text |
| `transformaciones` | `_2016/eola/chapter3.py` | A matrix moves î and ĵ | Faint fixed grid + bright moving grid; `apply_matrix` and `M @ v` in one `play` |
| `fourier` | `_2018/fourier.py` | Winding a signal finds its frequency | Two views, one tracker: wound curve + center of mass graph that grows |
| `choques` | `_2019/clacks` | Collisions count the digits of π | Event simulation; `state(t)` with `bisect`; `Integer` counter; fade + table |
| `espirales` | `_2019/spirals.py` | Primes in polar coordinates | 1000 `Dot`s, then 250 000 points in one `PMobject`; zoom out by scale |
| `epidemia` | `_2020/sir.py` | S, I and R | Simulation saved in arrays; dots + stacked areas driven by one step tracker |
| `limite-central` | `_2023/clt` | Sum of dice → bell curve | Exact convolution; bars at mean 0 and deviation 1; the bell and its formula last |
| `palabras-vectores` | `_2024/transformers/embedding.py` | Words as vectors (3D) | Axes with `curve`; flat labels at projected points; lists that `always_redraw` reads |
| `rectangulo-inscrito` | `_2024/inscribed_rect` | Pairs on a loop → a surface (3D) | One pair first (two dots, a lift), then all pairs as a `surface` |
| `paralaje` | `_2025/cosmic_distance/paralax.py` | Parallax gives distance (3D) | Perspective (`distance=14`); line of sight; `TracedPath` of the star on the far wall |
| `bola-peluda` | `_2026/hairy_ball` | Hairy ball theorem (3D) | Fibonacci sphere; only front arrows; `mix` tracker between two fields |
| `esfera` | `_2026/spheres_talk/volumes.py` | Area 4πr² and volume 4/3 πr³ (3D) | Sphere as bands; `spread` tracker opens it; `radius` tracker grows it in layers |

## The beats of each port

The captions of a port are its script. Read them in order and you have the story:

- `fourier`: a signal that beats 3 times per second → wind it around a point → at 3 turns per
  second the center of mass goes away → the peak gives the frequency of the signal.
- `choques`: a block of 100 kg pushes one of 1 kg against a wall → (31 collisions) → more zeros,
  more digits of π → table 31, 314, 3141 → π = 3,14159…
- `bola-peluda`: hair on a sphere, a tangent arrow at each point → at the poles the arrow is zero,
  a whirl → comb it in a different way: the whirls stay → you cannot comb a sphere without a
  whirl.
- `rectangulo-inscrito`: take two points of a closed loop → above their middle point, go up as
  much as their distance → all the pairs make a surface → the surface cuts itself → two pairs with
  the same middle and the same distance: a rectangle.

Each script has the same form: the object, an action, what we see, why it is true. Write the
captions of a new scene in this form before you write code, and show them to the user.

## Code to copy

**Event simulation (`choques`).** Exact for any number of events:

```python
def simulate(...):
    events = [(t, x1, v1, x2, v2, count)]
    while True:
        dt_block = (x2 - x1 - SMALL) / (v1 - v2) if v1 > v2 else np.inf
        dt_wall = -x1 / v1 if v1 < 0 else np.inf
        dt = min(dt_block, dt_wall)
        if dt == np.inf:
            return events
        ...  # move to the event, change the velocities, count + 1
        events.append((t, x1, v1, x2, v2, count))

EVENTS = simulate()
TIMES = [e[0] for e in EVENTS]

def state(time):
    t, x1, v1, x2, v2, count = EVENTS[bisect_right(TIMES, time) - 1]
    return x1 + v1 * (time - t), x2 + v2 * (time - t), count
```

**Simulation saved in arrays (`epidemia`).** The updater reads one row:

```python
POSITIONS, STATES = simulate(seed=3)          # shape (steps, people, 2) and (steps, people)

def update(group):
    i = int(step.get_value())
    for dot, p, s in zip(group, POSITIONS[i], STATES[i]):
        dot.move_to(CENTER + np.array([p[0], p[1], 0]) * HALF).set_color(COLORS[s])

people.add_updater(update)
scene.play(step.animate.set_value(STEPS - 1), run_time=9, rate_func=linear)
people.clear_updaters()
```

**Center of mass of a wound signal (`fourier`).** A Fourier transform in one line:

```python
def center_of_mass(f):
    z = np.mean(g(TS) * np.exp(-2j * np.pi * f * TS))
    return np.array([z.real, z.imag, 0])
```

**Sum of n dice (`limite-central`).**

```python
p = DIE
for _ in range(n - 1):
    p = np.convolve(p, DIE)
sums = np.arange(n, 6 * n + 1)
x = (sums - n * MEAN) / (SIGMA * np.sqrt(n))   # mean 0, deviation 1
height = p * SIGMA * np.sqrt(n)                # area of each bar = its probability
```

**Front of a sphere (`bola-peluda`).** Only what the camera sees:

```python
front = view(POINTS, yaw, PITCH)[:, 2] < 0
starts = project(POINTS * 1.01, yaw, PITCH, SCALE, CENTER)
ends = project(POINTS * 1.01 + vectors, yaw, PITCH, SCALE, CENTER)
arrows = VGroup(*[Arrow(s, e, buff=0, ...) for s, e, ok in zip(starts, ends, front)
                  if ok and np.linalg.norm(e - s) > 0.04])
```

**Fibonacci sphere (`bola-peluda`).**

```python
i = np.arange(n) + 0.5
z = 1 - 2 * i / n
phi = np.pi * (1 + 5 ** 0.5) * i
r = np.sqrt(1 - z * z)
points = R * np.column_stack([r * np.cos(phi), r * np.sin(phi), z])
```

**A tangent field on a sphere (`bola-peluda`).** Remove the normal part of any vector:
`v - p * (v @ p) / R²`. The spin around z is `np.cross([0, 0, 1], p)`.

**Primes to n (`espirales`).**

```python
sieve = np.ones(n + 1, dtype=bool)
sieve[:2] = False
for i in range(2, int(n ** 0.5) + 1):
    if sieve[i]:
        sieve[i * i::i] = False
primes = np.nonzero(sieve)[0]
```

**Hilbert curve (`hilbert`).** `_d2xy(n, d)` gives the cell of step `d` on an n×n grid. Draw the
cells with `VMobject().set_points_as_corners(points)`.

## What the ports do not do

Some techniques of 3Blue1Brown are not in the ports. Do not try them without a reason:

- No `ThreeDScene` or real 3D camera: all the 3D is `view3d.py` in a 2D scene.
- No characters (the "Pi creatures") and no copies of the look of a 3Blue1Brown video: use the
  talk's `style.py`. Put the credit in the `end` scene ("Original animation: 3Blue1Brown"), as the
  ports do.
- No ManimGL: the talks use Manim Community. The engine can try `scene_gx.py`, but write the
  scene for Manim CE.
