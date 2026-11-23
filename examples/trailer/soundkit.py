"""Music and sound effects for a video: notes, instruments, drums and effects, mixed on a
timeline that knows where the scenes of the video start.

    from soundkit import Mix, cuts, note, pad, kick, whoosh, pop
    starts = cuts()                          # {"logo": 0.0, "montage": 4.5, …} from the renders
    mix = Mix(76)                            # seconds
    mix.add(pad(["D3", "F#3", "A3"], 4), at=0)
    mix.add(whoosh(0.6), at=starts["montage"] - 0.5, pan=-0.3)
    mix.save("sound.m4a")                    # then: studio <video> info --music sound.m4a

Each sound is a mono numpy array at RATE samples a second. It runs in the environment of the
video (numpy, scipy and av come with Manim): uv run python sound.py
"""

import json
import re
import subprocess
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

RATE = 44100
_rng = np.random.default_rng(7)
NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


# ── notes and envelopes ──

def note(name):
    """The MIDI number of a note: "A4" is 69, "F#3" is 54, "Bb2" is 46. A number stays a number."""
    if not isinstance(name, str):
        return name
    m = re.fullmatch(r"([A-G])([#b]?)(-?\d)", name)
    if not m:
        raise ValueError(f"Not a note: {name}")
    shift = {"#": 1, "b": -1, "": 0}[m.group(2)]
    return 12 * (int(m.group(3)) + 1) + NAMES[m.group(1)] + shift


def hz(name):
    return 440.0 * 2 ** ((note(name) - 69) / 12)


def samples(seconds):
    return max(1, int(seconds * RATE))


def envelope(n, attack=0.005, release=0.1):
    """Rises in `attack` seconds, falls to 0 in the last `release` seconds."""
    e = np.ones(n)
    a, r = min(n, samples(attack)), min(n, samples(release))
    e[:a] = np.linspace(0, 1, a)
    e[n - r:] *= np.linspace(1, 0, r)
    return e


def decay(n, seconds):
    """An exponential fall: down to 1/1000 in `seconds`."""
    return np.exp(-np.arange(n) / RATE * 6.9 / seconds)


def band(x, low=None, high=None, order=2):
    """The sound with only the frequencies between low and high (Hz)."""
    if low and high:
        return sosfilt(butter(order, [low, high], "band", fs=RATE, output="sos"), x)
    if low:
        return sosfilt(butter(order, low, "high", fs=RATE, output="sos"), x)
    return sosfilt(butter(order, high, "low", fs=RATE, output="sos"), x)


def noise(seconds):
    return _rng.standard_normal(samples(seconds))


# ── instruments ──

WAVES = {
    "sine": lambda ph: np.sin(2 * np.pi * ph),
    "square": lambda ph: np.sign(np.sin(2 * np.pi * ph)) * 0.6,
    "triangle": lambda ph: 2 * np.abs(2 * (ph % 1) - 1) - 1,
    "saw": lambda ph: (2 * (ph % 1) - 1) * 0.6,
}


def tone(name, seconds, wave="sine", attack=0.005, release=0.15, glide=None):
    """One note. `glide` is the note it slides to (a pitch bend)."""
    n = samples(seconds)
    f = np.full(n, hz(name)) if glide is None else np.geomspace(hz(name), hz(glide), n)
    return WAVES[wave](np.cumsum(f) / RATE) * envelope(n, attack, release)


def pad(names, seconds, wave="saw", bright=1800):
    """A soft chord that holds, for the harmony below everything."""
    x = sum(tone(nm, seconds, wave, attack=min(0.4, seconds / 3), release=min(0.5, seconds / 3))
            for nm in names)
    return band(x / len(names), high=bright) * 0.8


def pluck(name, seconds=1.0, bright=5000):
    """A plucked string (Karplus-Strong)."""
    n, period = samples(seconds), max(2, int(RATE / hz(name)))
    out = np.zeros(n)
    out[:period] = _rng.uniform(-1, 1, period)
    for i in range(period, n):
        out[i] = 0.996 * 0.5 * (out[i - period] + out[i - period + 1])
    return band(out, high=bright) * envelope(n, 0.001, 0.05)


def bell(name, seconds=1.5):
    """A bell: a tone with a metallic partial, that rings out."""
    n = samples(seconds)
    t = np.arange(n) / RATE
    f = hz(name)
    return (np.sin(2 * np.pi * f * t + 1.6 * np.sin(2 * np.pi * f * 3.5 * t) * decay(n, seconds / 2))
            * decay(n, seconds) * 0.5)


def chip(names, step=0.125, wave="square"):
    """An 8-bit arpeggio: the notes one after another, `step` seconds each."""
    return np.concatenate([tone(nm, step, wave, attack=0.002, release=0.02) for nm in names]) * 0.5


# ── drums ──

def kick():
    n = samples(0.35)
    return np.sin(2 * np.pi * np.cumsum(np.geomspace(150, 45, n)) / RATE) * decay(n, 0.3)


def snare():
    x = band(noise(0.2), 1500, 8000) * decay(samples(0.2), 0.15) * 0.5
    body = tone("D3", 0.1) * 0.3
    x[:len(body)] += body
    return x


def clap():
    x = band(noise(0.25), 900, 6000) * decay(samples(0.25), 0.18)
    for k in (0.01, 0.02):  # a clap is three hands close together
        x[samples(k):] += x[:-samples(k)] * 0.6
    return x * 0.4


def hat(open_=False):
    length = 0.3 if open_ else 0.06
    return band(noise(length), 7000) * decay(samples(length), length) * 0.3


# ── sound effects ──

def sweep(x, start, end, width=0.5):
    """`x` through a band that moves from `start` Hz to `end` Hz: the sound of something moving."""
    out, zi = np.zeros_like(x), None
    chunks = np.array_split(np.arange(len(x)), max(1, len(x) // 512))
    for f, idx in zip(np.geomspace(start, end, len(chunks)), chunks):
        sos = butter(2, [f * (1 - width), f * (1 + width)], "band", fs=RATE, output="sos")
        zi = np.zeros((sos.shape[0], 2)) if zi is None else zi
        out[idx], zi = sosfilt(sos, x[idx], zi=zi)
    return out


def whoosh(seconds=0.6, up=True):
    """Air that passes: something flies in (up) or leaves (down)."""
    n = samples(seconds)
    shape = np.sin(np.linspace(0, np.pi, n)) ** 2
    low, high = (300, 3500) if up else (3500, 300)
    return sweep(noise(seconds), low, high) * shape * 1.6


def riser(seconds=1.0):
    """Tension before a cut: noise and a tone that both go up."""
    n = samples(seconds)
    rise = np.linspace(0, 1, n) ** 2
    return (sweep(noise(seconds), 400, 6000) * 0.8 + tone("A3", seconds, "saw", glide="A5") * 0.15) * rise


def impact():
    """A hit on a cut: a low thump and a burst of noise."""
    x = band(noise(0.8), 200, 3000) * decay(samples(0.8), 0.5) * 0.4
    k = kick()
    x[:len(k)] += k * 1.2
    return x


def pop(name="C6"):
    """Something appears: a short drop in pitch."""
    return tone(name, 0.09, glide=note(name) - 14, release=0.04) * 0.8


def click():
    """A button: a very short tick."""
    return band(noise(0.012), 2000, 9000) * decay(samples(0.012), 0.01) * 1.5


def blip(name="E6"):
    """An 8-bit beep, for a counter or a menu."""
    return tone(name, 0.07, "square", attack=0.001, release=0.02) * 0.5


def sparkle(seconds=0.8, root="E6"):
    """Little high bells that fall over each other: something becomes new."""
    out = np.zeros(samples(seconds + 0.6))
    steps = [0, 4, 7, 12, 16, 19]
    for i, k in enumerate(steps):
        b = bell(note(root) + k, 0.6) * 0.5
        at = samples(i * seconds / len(steps))
        out[at:at + len(b)] += b
    return out


def typing(keys=8, speed=0.09):
    """Keys of a keyboard, one after another."""
    out = np.zeros(samples(keys * speed + 0.05))
    for i in range(keys):
        at = samples(i * speed * _rng.uniform(0.8, 1.2))
        k = click() * _rng.uniform(0.5, 1.0)
        out[at:at + len(k)] += k
    return out


# ── the mix ──

class Mix:
    """A stereo timeline of `seconds`. `add` puts a sound at a time, with a gain and a pan (-1
    left, 1 right); `save` makes it loud enough without clipping and writes the file."""

    def __init__(self, seconds):
        self.n = samples(seconds)
        self.left, self.right = np.zeros(self.n), np.zeros(self.n)

    def add(self, sound, at, gain=1.0, pan=0.0):
        i = int(round(at * RATE))
        k = min(len(sound), self.n - i)
        if i < 0 or k <= 0:
            return self
        self.left[i:i + k] += sound[:k] * gain * np.sqrt((1 - pan) / 2)
        self.right[i:i + k] += sound[:k] * gain * np.sqrt((1 + pan) / 2)
        return self

    def stereo(self):
        mix = np.stack([self.left, self.right], 1)
        peak = np.abs(mix).max() or 1.0
        return np.tanh(mix / peak * 1.4) * 0.89  # a soft limiter

    def save(self, path):
        """A .wav, or any format that ffmpeg makes from it (.m4a, .mp3)."""
        import wave
        path = Path(path)
        wav = path.with_suffix(".wav")
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes((self.stereo() * 32767).astype("<i2").tobytes())
        if path.suffix != ".wav":
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-b:a", "192k", str(path)], check=True)
            wav.unlink()
        return path


def cuts(folder="."):
    """Where each scene of the video starts, in seconds, from its renders: {name: start}."""
    import av
    folder = Path(folder)
    names = re.findall(r"^\s*self\.slide_(\w+)\(\)", (folder / "main.py").read_text("utf-8"), re.M)
    starts, at = {}, 0.0
    for name in names:
        starts[name] = at
        data = json.loads((folder / ".termina" / f"{name}.json").read_text("utf-8"))
        for part in data.get("slides", []):
            with av.open(str(folder / part["file"].replace("\\", "/"))) as c:
                at += float(c.duration / av.time_base)
    return starts


def meter(path, start, seconds, fps=60, bands=14):
    """How loud the music is in `bands` bands, from low to high, `fps` times a second: an array
    frames x bands from 0 to 1. For an equalizer that moves with the real music."""
    import av
    with av.open(str(path)) as c:
        res = av.AudioResampler(format="flt", layout="mono", rate=RATE)
        pcm = np.concatenate([f.to_ndarray().ravel() for fr in c.decode(audio=0) for f in res.resample(fr)])
    edges = np.geomspace(60, 9000, bands + 1)
    freqs = np.fft.rfftfreq(2048, 1 / RATE)
    rows = []
    for k in range(int(seconds * fps)):
        i = samples(start + k / fps)
        win = pcm[i:i + 2048]
        spec = np.abs(np.fft.rfft(np.pad(win, (0, 2048 - len(win))) * np.hanning(2048)))
        rows.append([spec[(freqs >= a) & (freqs < b)].mean() for a, b in zip(edges, edges[1:])])
    db = 20 * np.log10(np.array(rows) + 1e-6)
    return np.clip((db - db.max(axis=0) + 30) / 30, 0, 1)  # each band by its own loudest moment
