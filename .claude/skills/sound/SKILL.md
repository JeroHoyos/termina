---
name: sound
description: Makes the music and the sound effects of a Termina video or reel (a soundtrack, a jingle, whooshes, pops, clicks, risers, hits) and puts them on the cuts of its scenes. Use it when the user asks for music, a soundtrack, sound effects, SFX or "sound" for a video, a reel or a trailer, or wants the music to follow the scenes. Use it with the `slides` skill, which says how to render and export.
---

# Music and sound effects for a video

A video of Termina has one sound file under its MP4: the `music` of its `termina.json`. The
export plays it from the start of the video. This skill makes that file with code, so the
music and the effects fall on the cuts of the scenes.

The tools are in `examples/trailer/soundkit.py`. Copy it into the folder of the video. It needs
numpy, scipy and av, which come with Manim in the environment of every talk.

## Flow

1. Render the scenes first. `cuts()` reads the start of each scene from the renders, so the
   sounds follow the real lengths. Render again, then make the sound again, if a scene changes
   its length.
2. Write `sound.py` in the folder of the video:

   ```python
   from soundkit import Mix, cuts, pad, kick, whoosh, pop, impact

   at = cuts()                              # {"title": 0.0, "idea": 4.2, …}
   end = 30                                 # the length of the video, in seconds
   mix = Mix(end)
   for name, start in at.items():           # a hit on every cut
       mix.add(impact(), start, gain=0.5)
   mix.add(whoosh(0.6), at["idea"] - 0.5, pan=-0.4)
   mix.save("sound.m4a")
   ```

3. Run it in that folder: `uv run python sound.py`.
4. Make it the music of the video: `studio <video> info --music sound.m4a`.
5. Export only when the user asks: `studio <video> export --mp4`.

## What soundkit gives

| Kind | Functions |
| --- | --- |
| Notes | `note("F#3")` is a MIDI number, `hz("A4")` is 440 |
| Instruments | `tone(note, s, wave)` (sine, square, triangle, saw; `glide` bends it), `pad(notes, s)`, `pluck(note)`, `bell(note)`, `chip(notes)` (8-bit arpeggio) |
| Drums | `kick()`, `snare()`, `clap()`, `hat(open_=False)` |
| Effects | `whoosh(s, up)`, `riser(s)`, `impact()`, `pop(note)`, `click()`, `blip(note)`, `sparkle(s)`, `typing(keys)` |
| Tools | `envelope`, `decay`, `band(x, low, high)`, `noise(s)`, `sweep(x, start_hz, end_hz)` |
| Timeline | `Mix(seconds).add(sound, at, gain, pan)`, `save("x.m4a")`, `cuts()` |
| For a scene | `meter(file, start, seconds, fps, bands)`: how loud each band is, frame by frame, for an equalizer that moves with the music |

Each sound is a mono numpy array at `RATE` (44100) samples a second. A new sound is a function
that returns one: add it to the `sound.py` of the video.

## Rules

- **Effects on what moves.** A whoosh starts about half its length before a thing arrives; a pop
  or a click falls on the frame where a thing appears or is pressed; a riser ends on the cut.
- **The music on the beat.** At 120 beats a minute a bar is 2 s: start the scenes on bars when
  you can, and put the drums on the beats.
- **Quiet effects.** Gain 0.2 to 0.5 for effects under music; louder only for one big moment.
- **Pan to the place.** An effect of a thing on the left of the frame gets a pan near -0.5.
- **Few effects.** One effect for each thing that moves on purpose, not for every small motion.
- **Your own sounds only.** Make every sound with code. Do not put songs or samples from other
  places in a video.

`examples/trailer/music.py` is a full soundtrack made this way: chords that follow the scenes,
drums, a melody, the 8-bit tune of the app and the effects of `soundkit.py`.
