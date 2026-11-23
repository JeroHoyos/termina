"""Soundtrack of the Termina trailer: pop, D major, 120 BPM, with full harmony.

A warm pad plays every chord with smooth voice leading, the bass walks down D C# B G, the hook has a
second voice a third below, plucked arpeggios fill the verses, and a bell plays a chord tone as each
letter of the logo draws. The cues match the scenes of the trailer. It writes music.m4a, the
music of the video (see termina.json). The sound effects come from soundkit.py. Run it in
this folder, then render the reels scene again (its equalizer reads the music), here and in
../trailer-reel, which gets a copy of the music:
    uv run python music.py
"""
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from scipy.ndimage import maximum_filter1d
from scipy.signal import butter, fftconvolve, lfilter, sosfilt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "engine"))
import soundkit as sfx  # noqa: E402  (the sound effects, in this folder)
import studio  # noqa: E402  (the 8-bit tune of the app: seed 35 = D major, 120 BPM, D A Bm G)

SR = 44100
DUR = 76.0
CUT = 4.0  # the seconds of the find scene, cut from the music at THEMES (see the end)
N = int(SR * DUR)
L = np.zeros(N)
R = np.zeros(N)
BEAT, BAR = 0.5, 2.0
rng = np.random.default_rng(3)

# chords: name -> (bass pitch class, pitch classes)
CH = {
    'D': (2, (2, 6, 9)), 'Dadd9': (2, (2, 6, 9, 4)), 'Dmaj9': (2, (2, 6, 9, 1, 4)),
    'A/C#': (1, (9, 1, 4)), 'A': (9, (9, 1, 4)), 'Asus4': (9, (9, 2, 4)), 'A7sus4': (9, (9, 2, 4, 7)),
    'Bm7': (11, (11, 2, 6, 9)), 'Gmaj7': (7, (7, 11, 2, 6)), 'G': (7, (7, 11, 2)),
    'Em7': (4, (4, 7, 11, 2)), 'F#m7': (6, (6, 9, 1, 4)),
}
# the chords bar by bar, from 4.5 s (a bar is 2 s)
PLAN = (['D', 'Bm7', 'Gmaj7'] +                                       # 4.5  montage
        ['D', 'Bm7', 'Gmaj7', 'Asus4', 'Gmaj7', 'A'] +                # 10.5 use cases
        ['Bm7', 'Gmaj7', 'A'] +                                       # 22.5 one slide
        ['Em7', 'A7sus4'] +                                           # 28.5 the app
        ['D', 'A/C#', 'Bm7', 'Gmaj7', 'D', 'A/C#', 'Bm7'] +           # 32.5 guide, chorus
        ['Gmaj7', 'A', 'Bm7'] +                                       # 46.5 Claude
        ['G', 'A', 'F#m7', 'Bm7', 'Em7'] +                            # 52.5 themes, export
        ['D', 'A', 'Bm7'] +                                           # 62.5 reels, 8-bit
        ['Dadd9', 'Dadd9', 'Dadd9'])                                  # 68.5 end
T0 = 4.5
WORDS, USES, ONE, APP, GUIDE, CLAUDE, THEMES, REELS, END = 4.5, 10.5, 22.5, 28.5, 32.5, 46.5, 52.5, 62.5, 68.5


def chord_at(t):
    return PLAN[min(len(PLAN) - 1, max(0, int((t - T0) // BAR)))]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def filt(x, f, kind, order=2):
    return sosfilt(butter(order, f, kind, fs=SR, output='sos'), x)


def add(sig, start, pan=0.0, gain=1.0):
    i = int(round(start * SR))
    n = min(len(sig), N - i)
    if n <= 0 or i < 0:
        return
    L[i:i + n] += sig[:n] * gain * np.sqrt(1 - pan)
    R[i:i + n] += sig[:n] * gain * np.sqrt(1 + pan)


def tail(n, r=0.01):
    e = np.ones(n)
    k = min(n, int(r * SR))
    e[n - k:] = np.linspace(1, 0, k)
    e[:min(n, 40)] *= np.linspace(0, 1, min(n, 40))
    return e


def x_of(n):
    return np.arange(n) / SR


def near(pc, center):
    """The note of pitch class pc nearest to the midi note center."""
    m = center - ((center - pc) % 12)
    return m + 12 if center - m > 6 else m


def voicing(name, center=62):
    """The chord's notes, each in the octave nearest to center: neighbor chords move little."""
    return sorted(near(pc, center) for pc in CH[name][1])


def bass_note(name):
    return near(CH[name][0], 41)


DEG = (0, 2, 4, 5, 7, 9, 11)  # D major, from D


def third_below(m):
    """The note two steps down the D major scale (a diatonic third)."""
    pc = (m - 2) % 12
    i = min(range(7), key=lambda k: abs(DEG[k] - pc))
    j = (i - 2) % 7
    return m - ((DEG[i] - DEG[j]) % 12)


# --- instruments -----------------------------------------------------------------------
def pluck(m, n, decay=0.996, bright=6000):
    p0 = max(2, int(round(SR / hz(m) - 0.5)))
    burst = np.zeros(n)
    burst[:p0] = filt(rng.uniform(-1, 1, p0), bright, 'low')
    a = np.zeros(p0 + 2)
    a[0], a[p0], a[p0 + 1] = 1.0, -decay / 2, -decay / 2
    return lfilter([1.0], a, burst)


def strum(notes, length, gain=0.5, mute=False, bright=5000):
    n = int(length * SR)
    out = np.zeros(n + 4000)
    for k, m in enumerate(notes):
        d = int(k * 0.008 * SR)
        out[d:d + n] += pluck(m, n, 0.95 if mute else 0.996, 1800 if mute else bright)
    return filt(out[:n], 90, 'high') * tail(n, .04) * gain * 0.5


def guitar(name):
    """A guitar voicing: the bass, then the chord an octave above the pad."""
    v = voicing(name, 60)
    return [bass_note(name) + 12] + v + [v[0] + 12]


def pad(name, length, gain=0.16, attack=0.25, center=62):
    """A warm pad: three detuned saws per note, low-passed, slow in and out."""
    n = int(length * SR)
    x = x_of(n)
    s = np.zeros(n)
    for m in voicing(name, center):
        for d in (-7, 0, 7):
            ph = np.cumsum(np.full(n, hz(m) * 2 ** (d / 1200) / SR)) + rng.random()
            s += 2 * (ph % 1) - 1
    s = filt(s, 1500, 'low', 4)
    env = np.minimum(1, x / attack) * np.minimum(1, (length - x) / 0.25)
    return s * env * gain / 6


def bass(m, length, gain=0.6):
    n = int(length * SR)
    x = x_of(n)
    s = np.sin(2 * np.pi * hz(m) * x) + 0.25 * np.sin(4 * np.pi * hz(m) * x) + 0.08 * np.sin(6 * np.pi * hz(m) * x)
    return s * np.exp(-x * 2.2) * tail(n, 0.02) * gain


def kick(gain=1.0):
    n = int(0.4 * SR)
    x = x_of(n)
    s = np.sin(2 * np.pi * (48 * x + 140 * (1 - np.exp(-30 * x)) / 30)) * np.exp(-x * 9)
    s[:150] += rng.standard_normal(150) * 0.3 * np.linspace(1, 0, 150)
    return s * gain


def clap(gain=0.45):
    n = int(0.3 * SR)
    x = x_of(n)
    noise = filt(rng.standard_normal(n), 1100, 'high')
    burst = sum(np.exp(-np.clip(x - d, 0, None) * 160) * (x >= d) for d in (0, .011, .022))
    return noise * (burst * 0.6 + np.exp(-x * 14) * 0.5) * gain


def hat(gain=0.12, open_=False):
    n = int((0.25 if open_ else 0.05) * SR)
    x = x_of(n)
    return filt(rng.standard_normal(n), 8000, 'high') * np.exp(-x * (12 if open_ else 70)) * gain


def crash(gain=0.3):
    n = int(2.5 * SR)
    x = x_of(n)
    return filt(rng.standard_normal(n), 4500, 'high') * np.exp(-x * 1.6) * gain


def snap(gain=0.9):
    n = int(0.12 * SR)
    x = x_of(n)
    tick = filt(rng.standard_normal(n), 2500, 'high') * np.exp(-x * 400)
    tick2 = np.roll(filt(rng.standard_normal(n), 5000, 'high') * np.exp(-x * 600), int(0.018 * SR)) * 0.7
    body = np.sin(2 * np.pi * 1800 * x) * np.exp(-x * 220) * 0.5
    return (tick + tick2 + body) * gain


def bell(m, length=1.6, gain=0.14):
    """A soft FM bell."""
    n = int(length * SR)
    x = x_of(n)
    mod = np.sin(2 * np.pi * hz(m) * 3.5 * x) * 1.6 * np.exp(-x * 6)
    return np.sin(2 * np.pi * hz(m) * x + mod) * np.exp(-x * 2.8) * tail(n, .05) * gain


def lead(m, length, gain=0.2):
    n = int(length * SR)
    x = x_of(n)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * x) * np.clip(x * 4, 0, 1)
    ph = np.cumsum(hz(m) * vib / SR)
    s = np.sin(2 * np.pi * ph) + 0.25 * np.sin(4 * np.pi * ph) + 0.3 * (4 * np.abs(ph % 1 - 0.5) - 1)
    s = s * np.minimum(1, x * 80) * np.exp(-x * 1.6)
    return s * tail(n, .03) * gain


def riser(length, gain=0.3):
    n = int(length * SR)
    k = np.linspace(0, 1, n)
    return filt(rng.standard_normal(n), 1500, 'high') * k ** 3 * gain


def roll(start, length):
    t, step = 0.0, BEAT / 2
    while t < length:
        add(clap(0.15 + 0.35 * t / length), start + t, pan=0.1)
        t += step
        if t > length / 2:
            step = BEAT / 4


def melody(bars, b0, gain=0.2, harmony=True):
    """Eighth notes, one list per bar, from b0; a second voice a third below, softer."""
    for k, notes in enumerate(bars):
        for e, m in enumerate(notes):
            if m is None:
                continue
            t = b0 + k * BAR + e * BEAT / 2
            add(lead(m, BEAT / 2 * 1.7, gain), t, pan=0.12)
            if harmony:
                add(lead(third_below(m), BEAT / 2 * 1.7, gain * 0.55), t, pan=-0.2)


# --- the arrangement, bar by bar -------------------------------------------------------
def drums(b0, energy):
    """energy 0: hats only, 1: kick and claps, 2: full, with open hats."""
    for e in range(8):
        add(hat(0.08 if e % 2 else 0.12), b0 + e * BEAT / 2, pan=0.35)
    if energy == 0:
        return
    for q in range(4):
        add(kick(0.9), b0 + q * BEAT)
        if q in (1, 3):
            add(clap(0.4), b0 + q * BEAT, pan=-0.05)
    if energy == 2:
        add(hat(0.1, open_=True), b0 + 3.5 * BEAT, pan=0.4)


def harmony_bar(b0, energy):
    """The pad and the bass of one bar; arpeggios, strums by energy."""
    name = chord_at(b0 + 0.01)
    add(pad(name, BAR + 0.15, 0.13 + 0.03 * energy), b0)
    root = bass_note(name)
    for e in range(8):
        # a root on the beats; on the last eighth, a step to the next bass note (a walking line)
        nxt = bass_note(chord_at(b0 + BAR + 0.01))
        m = root if e < 7 or nxt == root else root + (1 if nxt > root else -1) * (1 if abs(nxt - root) <= 2 else 2)
        add(bass(m - 12 if e % 2 == 0 else m, BEAT / 2 * 0.92, 0.6 if e % 2 == 0 else 0.45), b0 + e * BEAT / 2)
    v = voicing(name, 66)
    if energy == 1:  # plucked arpeggio in sixteenths
        order = [0, 1, 2, len(v) - 1, 2, 1] * 3
        for s in range(16):
            add(pluck(v[order[s] % len(v)] + 12, int(0.35 * SR), 0.993, 4000) * 0.22, b0 + s * BEAT / 4, pan=0.35 * (-1) ** s)
    if energy == 2:  # open strums
        for at, g in ((0, .34), (1.0, .24), (1.5, .26), (2.5, .22), (3.0, .26), (3.5, .22)):
            add(strum(guitar(name), 0.9, g), b0 + at * BEAT, pan=-0.45)
            add(strum(guitar(name), 0.9, g * 0.8), b0 + at * BEAT + 0.012, pan=0.45)


# intro: a pad swells on Dmaj9, two snaps build the logo, a bell for each letter of the word
add(pad('Dmaj9', 4.6, 0.12, attack=2.0, center=60), 0.3)
add(snap(), 1.0)
add(snap(0.8), 1.5, pan=0.15)
for i, m in enumerate((62, 66, 69, 73, 76, 81)):  # D F# A C# E A, up with the letters
    add(bell(m, 1.8, 0.11), 2.45 + i * 0.09, pan=-0.5 + 0.2 * i)
add(bell(86, 2.2, 0.1), 3.15)  # the dot of the i
add(riser(1.2, 0.25), WORDS - 1.2)
add(crash(0.35), WORDS)

b = WORDS
while b < USES - 0.01:  # montage: the pad, bass and kick, a chord stab on every cut
    harmony_bar(b, 0)
    drums(b, 1)
    b += BAR
for cut in (4.5, 5.5, 6.5, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0):
    add(strum(guitar(chord_at(cut + 0.01)), 0.35, 0.28, mute=True), cut, pan=0.2)

add(crash(0.25), USES)
while b < ONE - 0.01:  # use cases: the arpeggios
    harmony_bar(b, 1)
    drums(b, 1)
    b += BAR
for t in (13.5, 16.5, 19.5):
    add(snap(0.5), t, pan=0.3)
melody([[None] * 6 + [69, 71], [74, None, 73, 71, 69, None, 66, None], [67, None, 66, 64, 62, None, None, None]], 16.5, 0.13)

# one slide: half time, pad and arpeggio; the render rises, and a chord rings when it is done
while b < APP - 0.01:
    harmony_bar(b, 1)
    drums(b, 0)
    b += BAR
for i in range(16):
    add(bell(62 + DEG[i % 7] + 12 * (i // 7), 0.4, 0.05 + 0.04 * i / 16), 24.9 + i * 1.9 / 16, pan=0.3 * np.sin(i))
add(strum(guitar('A'), 2.0, 0.3, bright=3000), 26.8)
add(bell(81, 1.5, 0.12), 26.8)

# the app: build into the drop
while b < GUIDE - 0.01:
    harmony_bar(b, 1)
    drums(b, 1)
    b += BAR
roll(GUIDE - 1.0, 1.0)
add(riser(2.0, 0.3), GUIDE - 2.0)

# guide: the chorus, with the hook and its second voice
HOOK = [[66, None, 69, 71, 73, 71, 69, None], [73, None, 73, 71, 69, None, 64, 66],
        [66, None, 66, 69, 71, 73, 74, None], [74, 73, 71, 69, None, 71, 69, 66],
        [66, None, 69, 71, 73, 71, 69, None], [73, None, 73, 74, 76, None, 73, None],
        [74, None, 73, 71, 69, 71, 73, None]]
add(crash(0.45), GUIDE)
k = 0
while b < CLAUDE - 0.01:
    harmony_bar(b, 2)
    drums(b, 2)
    if k % 4 == 0:
        add(crash(0.22), b)
    b += BAR
    k += 1
melody(HOOK, GUIDE, 0.19)
for t in (33.5, 37.1, 43.4, 45.35):  # the clicks of the cursor
    add(snap(0.45), t, pan=0.25)

# Claude: lighter, the arpeggios, then a bright chord on approve
while b < THEMES - 0.01:
    harmony_bar(b, 1)
    drums(b, 1)
    b += BAR
add(bell(78, 1.6, 0.12), 51.2)
add(bell(83, 1.6, 0.1), 51.32)
add(bell(86, 2.0, 0.1), 51.44)
roll(THEMES - 1.0, 1.0)

# themes and export: the second chorus, a new hook over G A F#m7 Bm7 Em7
HOOK2 = [[71, None, 71, 74, None, 71, 69, 67], [69, None, 69, 73, None, 76, 73, 69],
         [69, None, 69, 73, 76, None, 73, 69], [74, None, 73, 74, 76, None, 78, None],
         [79, None, 78, 76, 74, None, 71, None]]
while b < REELS - 0.01:
    harmony_bar(b, 2)
    drums(b, 2)
    b += BAR
melody(HOOK2, THEMES, 0.19)
add(riser(1.0, 0.25), REELS - 1.0)

# reels: the 8-bit tune of Termina leads; the pad and the bass play its chords below it
chip, what = studio.chiptune_samples(35)
chip = np.interp(np.arange(0, len(chip), 22050 / SR), np.arange(len(chip)), np.array(chip))
seg = int((END - REELS + 0.3) * SR)
chip = np.tile(chip, 2)[:seg] * tail(seg, 0.4) * 0.45
add(chip, REELS)
add(crash(0.4), REELS)
# the video turns into a reel and locks, the equalizer comes in, and the three effects of the
# chips sound as they pop up (slides/reels.py shows them at the same times)
add(sfx.whoosh(1.0, up=False), 64.0, gain=0.3)
add(sfx.click(), 65.0, gain=0.4)
add(sfx.sparkle(0.6, "D6"), 65.4, pan=0.3, gain=0.35)
add(sfx.whoosh(0.5), 66.2 - 0.25, pan=0.4, gain=0.4)
add(sfx.pop("D6"), 66.65, pan=0.4, gain=0.5)
add(sfx.click(), 67.1, pan=0.4, gain=0.6)
while b < END - 0.01:
    name = chord_at(b + 0.01)
    add(pad(name, BAR + 0.1, 0.1), b)
    add(bass(bass_note(name) - 12, BAR * 0.95, 0.5), b)
    for q in range(4):
        add(kick(0.6), b + q * BEAT)
        if q in (1, 3):
            add(clap(0.3), b + q * BEAT)
    b += BAR
roll(END - 1.0, 1.0)

# the end: a big D add9 that rings out, the bass on D, a bell arpeggio up, the last snap
add(crash(0.5), END)
add(kick(1.0), END)
add(snap(1.0), END + 0.05)
add(strum(guitar('Dadd9'), 6.5, 0.5, bright=2800), END, pan=-0.3)
add(strum(guitar('Dadd9'), 6.5, 0.4, bright=2800), END + 0.015, pan=0.3)
add(pad('Dadd9', 7.0, 0.16, attack=0.05, center=62), END)
add(bass(38, 5.0, 0.7), END)
for i, m in enumerate((74, 78, 81, 85, 86)):
    add(bell(m, 3.0, 0.1), END + 0.6 + i * 0.14, pan=0.2 * (i - 2))

# The find scene left the trailer: its two bars (52.5-56.5 s) leave the music, and a crash
# marks the cut. The scenes after it play 4 s earlier than the times above.
add(crash(0.45), THEMES + CUT)
gone = np.s_[int(THEMES * SR):int((THEMES + CUT) * SR)]
L, R = np.delete(L, gone), np.delete(R, gone)
N = len(L)

# --- room and master -------------------------------------------------------------------
ir_n = int(1.4 * SR)
ir = filt(rng.standard_normal(ir_n) * np.exp(-x_of(ir_n) * 4.5), 6000, 'low')
ir /= np.sqrt((ir ** 2).sum())
L, R = L + 0.2 * fftconvolve(L, ir)[:N], R + 0.2 * fftconvolve(R, np.roll(ir, 250))[:N]
fade = np.ones(N)
fade[-int(1.6 * SR):] = np.linspace(1, 0, int(1.6 * SR))
mix = np.stack([L, R], 1) * fade[:, None]
mix = mix / np.percentile(np.abs(mix), 99.5) * 0.6
peak = np.abs(mix).max(axis=1)
env = np.maximum(lfilter([0.002], [1, -0.998], np.maximum(maximum_filter1d(peak, size=int(0.006 * SR)), 0.85)),
                 maximum_filter1d(peak, size=int(0.006 * SR)))
gain = np.minimum(1.0, 0.85 / np.maximum(env, 1e-9))
gain = maximum_filter1d(gain[::-1], size=int(0.005 * SR))[::-1]
gain = lfilter([0.01], [1, -0.99], np.minimum(gain, 0.85 / np.maximum(peak, 1e-9)))
gain = np.minimum(gain, 0.89 / np.maximum(peak, 1e-9))
mix = mix * gain[:, None]
with wave.open(str(HERE / 'music.wav'), 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(HERE / 'music.wav'), '-c:a', 'aac', '-b:a', '192k',
                str(HERE / 'music.m4a')], check=True)
(HERE / 'music.wav').unlink()
shutil.copy(HERE / 'music.m4a', HERE.parent / 'trailer-reel' / 'music.m4a')  # the reel has the same music
print('8-bit:', what)
