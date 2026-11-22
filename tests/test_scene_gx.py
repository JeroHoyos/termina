"""Tests of engine/scene_gx.py without ManimGX or manim-slides: small fakes take their place."""

import importlib.util
import sys
import types
from pathlib import Path
from unittest import mock

import pytest

SCENE_GX = Path(__file__).resolve().parents[1] / "engine" / "scene_gx.py"


class Cut(Exception):
    pass


@pytest.fixture
def gx(monkeypatch):
    """scene_gx, imported with fake modules. The modules that it adds go away after the test."""
    fakes = {
        "manimgx": types.ModuleType("manimgx"),
        "manimgx.constants": types.ModuleType("manimgx.constants"),
        "manimgx.animation": types.SimpleNamespace(easing=types.ModuleType("easing")),
        "manimgx.config": types.SimpleNamespace(config=types.SimpleNamespace(frame_rate=30)),
        "manimgx.rendering.film": types.SimpleNamespace(
            DEFAULT_ENCODER_CRF=23, DEFAULT_ENCODER_PRESET="fast", Cut=Cut),
        "manim_slides.config": types.SimpleNamespace(
            BaseSlideConfig=lambda **options: options, PresentationConfig=None, SlideConfig=None),
        "manim_slides.utils": types.SimpleNamespace(reverse_video_file=None),
    }
    fakes["manimgx"].constants = fakes["manimgx.constants"]
    fakes["manimgx"].Scene = object
    fakes["manimgx"].Circle = "a circle"
    fakes["manimgx"].SingleStringMathTex = "tex"
    before = set(sys.modules)
    for name, module in fakes.items():
        monkeypatch.setitem(sys.modules, name, module)
    spec = importlib.util.spec_from_file_location("scene_gx", SCENE_GX)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    yield module
    for name in set(sys.modules) - before:
        del sys.modules[name]


def test_a_still_frame_goes_into_the_mp4_once_for_each_frame(gx):
    player = mock.Mock()
    gx._EachFrame(player).push("view", "records", repeat=3, key=True)
    assert player.push.call_args_list == [
        mock.call("view", "records", 1, (), True),
        mock.call("view", "records", 1, (), False),
        mock.call("view", "records", 1, (), False),
    ]


def test_manim_is_manimgx_for_the_talk(gx):
    gx._as_manim()
    import manim
    from manim.utils.exceptions import EndSceneEarlyException
    from manim_slides.slide import Slide

    assert manim.Circle == "a circle"
    assert manim.rate_functions is sys.modules["manim.utils.rate_functions"]
    assert EndSceneEarlyException is Cut
    assert Slide is gx.Slide


def slides(gx):
    """A Slide with a fake film, without ManimGX's setup."""
    s = gx.Slide.__new__(gx.Slide)
    s.film = types.SimpleNamespace(frame_count=0, _send=mock.Mock(), _player=mock.Mock())
    s._slides, s._current_animation, s._s_start = [], 0, 0
    s._s_video, s._base_slide_config = Path("videos/0.mp4"), {}
    return s


def test_each_pause_has_its_own_mp4(gx):
    s = slides(gx)
    s.next_slide(loop=True)  # nothing was drawn yet: no pause, only its options
    assert s._slides == [] and s._base_slide_config == {"loop": True}
    s.film.frame_count = 10
    s.next_slide()
    s.film.frame_count = 25
    s.next_slide()
    assert [p.video.name for p in s._slides] == ["0.mp4", "1.mp4"]
    assert [p.options for p in s._slides] == [{"loop": True}, {}]
    assert s._s_video.name == "2.mp4" and s._s_start == 25
    assert s.film._player.begin_export.call_count == 2


def test_a_skipped_slide_gives_no_frames(gx):
    s = slides(gx)
    s.renderer = types.SimpleNamespace(_original_skipping_status=True)
    draw = mock.Mock()
    s._s_unless_skipped(draw)(1)
    s.renderer._original_skipping_status = False
    s._s_unless_skipped(draw)(2)
    assert draw.call_args_list == [mock.call(2)]
