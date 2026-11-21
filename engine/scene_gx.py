"""scene.py, drawn by ManimGX in place of Manim CE: the same slides, faster.

It is not used by hand: studio.py launches it from a talk's `presentacion/` folder with

    uv run --with manimgx python <path>/scene_gx.py

and the variables of scene.py, plus STUDIO_QUALITY = 480p, 720p or 1080p.

The talk and scene.py import `manim` and `manim_slides.slide`. Here `manim` is ManimGX, and
`manim_slides.slide.Slide` is the Slide below: it does the part of manim-slides' Slide that
scene.py uses. Each pause goes to its own MP4 while the scene runs, and a slide is saved in the
format of manim-slides, so the presenter and the app do not see a difference. A talk that
imports a part of Manim CE that ManimGX does not have fails here, and studio.py draws it with
Manim CE.
"""

import hashlib
import os
import shutil
import sys
import tempfile
import types
from pathlib import Path

import manimgx
import manimgx.constants
from manimgx.animation import easing
from manimgx.config import config
from manimgx.rendering.film import DEFAULT_ENCODER_CRF, DEFAULT_ENCODER_PRESET, Cut

# Only the parts of manim-slides that do not import Manim CE.
from manim_slides.config import BaseSlideConfig, PresentationConfig, SlideConfig
from manim_slides.utils import reverse_video_file

QUALITIES = {"480p": (854, 480, 15), "720p": (1280, 720, 30), "1080p": (1920, 1080, 60)}


class _EachFrame:
    """ManimGX's player, but a frame that stays on screen goes into the MP4 once for each frame
    it lasts. ManimGX writes it once, with a long duration: then the frame rate is not constant,
    and the frame 0.1 s before the end, from which the app makes its pictures, is not found."""

    def __init__(self, player):
        self._player = player

    def __getattr__(self, name):
        return getattr(self._player, name)

    def push(self, view, records, repeat=1, cameras=(), key=False, capture=False):
        for i in range(repeat):
            self._player.push(view, records, 1, cameras, key and i == 0)


class Slide(manimgx.Scene):
    """manim-slides' Slide, as scene.py uses it."""

    disable_caching = flush_cache = skip_reversing = False
    renderer = None  # in place of ManimGX's property: scene.py marks skipped slides on it

    def setup(self):
        super().setup()
        self.renderer = types.SimpleNamespace(_original_skipping_status=False)
        self._output_folder = Path("slides")
        self._slides = []              # each pause: its MP4 and its options
        self._current_animation = 0
        self._base_slide_config = BaseSlideConfig()  # the options of the pause that is drawn now
        film = self.film
        self._s_video = Path(film.video)  # render() starts the MP4 of the first pause
        self._s_start = 0                 # the frame of the film where this pause starts
        for name in ("record", "tween"):
            setattr(film, name, self._s_unless_skipped(getattr(film, name)))
        film._player = _EachFrame(film._player)

    def _s_unless_skipped(self, draw):
        """A skipped slide gives no frames, as in Manim CE."""
        def method(*args, **kwargs):
            if not self.renderer._original_skipping_status:
                draw(*args, **kwargs)

        return method

    def play(self, *args, **kwargs):
        super().play(*args, **kwargs)
        self._current_animation += 1

    def next_slide(self, **options):
        """Closes the MP4 of this pause and starts the next one. As in manim-slides, the options
        are for the pause that starts. A talk can change them in `_base_slide_config`."""
        film = self.film
        if film.frame_count > self._s_start:
            film._send()  # the frame that waits to know how long it lasts
            film._player.end_export()
            self._slides.append(types.SimpleNamespace(
                video=self._s_video, options=self._base_slide_config,
                end_animation=self._current_animation))
            self._s_video = self._s_video.with_name(f"{len(self._slides)}.mp4")
            film._player.begin_export(str(self._s_video), fps=int(config.frame_rate),
                                      preset=DEFAULT_ENCODER_PRESET, crf=DEFAULT_ENCODER_CRF)
            self._s_start = film.frame_count
        self._base_slide_config = BaseSlideConfig(**options)

    def _save_slides(self, use_cache=True, flush_cache=False, skip_reversing=False):
        """Writes `<folder>/<scene>.json` and its videos, as manim-slides does."""
        folder = self._output_folder / "files" / str(self)
        folder.mkdir(parents=True, exist_ok=True)
        slides = []
        for pause in self._slides:
            name = hashlib.sha256(pause.video.read_bytes()).hexdigest()[:16]
            file, rev_file = folder / f"{name}.mp4", folder / f"{name}_reversed.mp4"
            shutil.copyfile(pause.video, file)
            if not rev_file.exists():
                reverse_video_file(file, rev_file, disable=True)
            slides.append(SlideConfig.from_pre_slide_config_and_files(pause.options, file, rev_file))
        PresentationConfig(slides=slides, resolution=(config.pixel_width, config.pixel_height),
                           background_color=self.camera.background_color.to_hex()
                           ).to_file(self._output_folder / f"{self}.json")


def _module(name, **names):
    module = types.ModuleType(name)
    module.__dict__.update(names)
    sys.modules[name] = module


def _as_manim():
    """`manim` is ManimGX, with the parts of Manim CE that scene.py and the talks import."""
    _module("manim", **{k: v for k, v in vars(manimgx).items() if not k.startswith("__")},
            rate_functions=easing)
    sys.modules["manim.constants"] = manimgx.constants
    _module("manim.utils", rate_functions=easing)
    sys.modules["manim.utils.rate_functions"] = easing
    _module("manim.utils.exceptions", EndSceneEarlyException=Cut)
    _module("manim.mobject")
    _module("manim.mobject.text")
    _module("manim.mobject.text.tex_mobject", SingleStringMathTex=manimgx.SingleStringMathTex)
    _module("manim_slides.slide", Slide=Slide)


def main():
    config.pixel_width, config.pixel_height, config.frame_rate = QUALITIES[os.environ["STUDIO_QUALITY"]]
    config.disable_caching = config.flush_cache = False  # scene.py reads them, as in Manim CE
    if os.environ.pop("STUDIO_VERTICAL", "") == "on":
        # A reel. ManimGX makes the frame of a tall video 8 units wide by itself, which is what
        # scene.py does for Manim CE.
        config.pixel_width, config.pixel_height = config.pixel_height, config.pixel_width
    _as_manim()
    sys.path.insert(0, str(Path(__file__).parent))
    import scene

    videos = Path(tempfile.mkdtemp(prefix="termina-gx-"))
    try:
        slides = scene.Slides()
        slides.render(videos / "0.mp4")
        slides._save_slides()
    finally:
        shutil.rmtree(videos, ignore_errors=True)


if __name__ == "__main__":
    main()
