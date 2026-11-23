"""The scenes of the reel. They are the scenes of the trailer (../trailer), laid out again on a
stage of 1080 x 1920: the kit, the colors, the fonts and the parts of each scene come from there,
and the times and the music are the same."""

import importlib.util
import sys
from pathlib import Path

TRAILER = Path(__file__).resolve().parents[2] / "trailer"
sys.path.insert(0, str(TRAILER))  # kit, style and soundkit
_spec = importlib.util.spec_from_file_location("trailer", TRAILER / "slides" / "__init__.py",
                                               submodule_search_locations=[str(TRAILER / "slides")])
sys.modules["trailer"] = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sys.modules["trailer"])

from . import app, claude, end, export, guide, logo, montage, one_slide, reels, uses  # noqa: E402


class SlideBase:
    def start_slide(self):
        """Each scene leaves the stage empty and the next one starts on a cut, on the beat of
        the music: no fade between them."""


def _slide(build):
    def method(self):
        self.start_slide()
        build(self)
        # The cut at the end of the scene. The video does not stop there.
        self.next_slide()

    return method


class TalkSlides:
    slide_logo = _slide(logo.build)
    slide_montage = _slide(montage.build)
    slide_uses = _slide(uses.build)
    slide_one_slide = _slide(one_slide.build)
    slide_app = _slide(app.build)
    slide_guide = _slide(guide.build)
    slide_claude = _slide(claude.build)
    slide_export = _slide(export.build)
    slide_reels = _slide(reels.build)
    slide_end = _slide(end.build)
