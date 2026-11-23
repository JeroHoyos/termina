# Termina trailer

The trailer of Termina, made with Termina: a video of 10 scenes and 72 seconds, with music.

Each scene is a function of the time on a stage of 1920 x 1080 pixels (`kit.py`). The scenes
start on the beat of `music.m4a`, so each one has an exact length. The scenes show rendered
slides of the other example talks. Render those slides first:

```powershell
termina\studio.cmd manimgx-examples render --pending
termina\studio.cmd fourier-circles render --pending
termina\studio.cmd strange-attractor render --pending
termina\studio.cmd trailer render --all
termina\studio.cmd trailer export --mp4
```

`music.py` makes `music.m4a` again, with the sound effects of `soundkit.py`: `uv run python music.py`. The fonts in `fonts/`
are Space Grotesk and IBM Plex Mono (SIL Open Font License).
