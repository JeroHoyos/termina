<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/images/wordmark-dark.svg">
    <img src="docs/images/wordmark.svg" width="440" alt="Termina">
  </picture>
</p>

<h3 align="center">Talks, videos and reels made with math.<br>One slide at a time, with Claude.</h3>

<p align="center">
  <img src="https://img.shields.io/badge/Windows%20%7C%20Linux%20(experimental)-111827?style=for-the-badge" alt="Windows and Linux" />
  <img src="https://img.shields.io/badge/open%20source-MIT-2b59ff?style=for-the-badge" alt="MIT license" />
  <img src="https://img.shields.io/badge/status-pre--release%200.6-b45309?style=for-the-badge" alt="Pre-release 0.6" />
</p>

<p align="center">
  <a href="docs/images/trailer.mp4"><img src="docs/images/trailer.gif" width="860" alt="The trailer of Termina"></a>
  <br>
  <a href="docs/images/trailer.mp4"><b>Watch the trailer with sound</b></a>
</p>

<p align="center">
  <img src="docs/images/termina.png" width="860" alt="The window of Termina: the slides, the slide video and the review, the Claude chat">
</p>

## Render one slide. Keep the others.

<p align="center"><img src="docs/images/features/render-one.jpg" width="760" alt="One slide changed, and only that slide renders again"></p>

## Mark it

<p align="center"><img src="docs/images/features/mark.jpg" width="760" alt="A point, a circle and an arrow on a slide"></p>

## Edit it yourself

<p align="center"><img src="docs/images/features/edit.jpg" width="760" alt="Boxes on the objects, a new title and a dragged counter"></p>

## Claude fixes it

<p align="center"><img src="docs/images/features/chat.jpg" width="760" alt="Claude reads the slide, edits it, renders it and looks at it"></p>

## Videos and reels, with music

<p align="center"><img src="docs/images/features/reels.jpg" width="760" alt="A 16:9 video becomes a 9:16 reel with 8-bit music"></p>

## Step by step

| | |
| --- | --- |
| <img src="docs/images/new-talk.png" width="420" alt="New talk"><br>**New talk** | <img src="docs/images/rendering.png" width="420" alt="Render"><br>**Render pending** |
| <img src="docs/images/mark.png" width="420" alt="Mark on the slide"><br>**Mark on the slide** | <img src="docs/images/review.png" width="420" alt="Review"><br>**Send to Claude** |
| <img src="docs/images/approved.png" width="420" alt="Approved"><br>**Approve** | <img src="docs/images/export.png" width="420" alt="Export"><br>**Export: HTML, PDF, MP4, GIF** |
| <img src="docs/images/new-slide.png" width="420" alt="New slide"><br>**New slide** | <img src="docs/images/web-panel.png" width="420" alt="Web panel"><br>**Web panel** |

## Examples

| [Drawing with circles](examples/fourier-circles/) | [A butterfly in the equations](examples/strange-attractor/) |
| --- | --- |
| <img src="docs/media/fourier-heart.gif" width="420" alt="Forty circles draw a heart"> | <img src="docs/media/lorenz-attractor.gif" width="420" alt="The Lorenz attractor"> |

## The folder of a talk

```text
my-talk/
  termina.json   what the talk is: title, topic, language, resolution
  main.py        the order of the slides
  style.py       the colors and the font
  slides/        the code of the slides, one .py file for each slide
  pictures/      the pictures that you add to the slides
  export/        your exports: HTML, PDF, MP4, PowerPoint
  .termina/      the renders. You can delete this folder. Termina renders the slides again.
```

If the folder holds more than the talk, for example practice notebooks, put the talk in
`my-talk/presentation/`. Termina changes the names of an older talk when it opens the talk:
`diapositivas/` becomes `slides/`, `diapos/` becomes `.termina/` and `talk.manimrs` becomes
`termina.json`. The renders stay correct.

## Installation

Pre-release: there is no installer. These programs are necessary: [uv](https://docs.astral.sh/uv/),
[FFmpeg](https://ffmpeg.org/), [Rust](https://rustup.rs/), [Node.js](https://nodejs.org/) 20+ and
[Claude Code](https://claude.com/claude-code). Clone it into the folder that holds your talks.

```powershell
git clone https://github.com/JeroHoyos/manimrs-studio.git termina
cd termina\frontend; npm ci; npm run build; cd ..
cargo build --release
.\target\release\termina.exe
```

## Contribution

Small pull requests. Before you send one: `uv run pytest`, `uv run complexipy .`, build the app.

## License

[MIT](LICENSE). Built on [Manim Community](https://www.manim.community/),
[ManimGX](https://github.com/academa-labs/manimgx) and
[Manim Slides](https://github.com/jeertmans/manim-slides). Not a part of those projects or of
Anthropic. Claude is a trademark of Anthropic.
