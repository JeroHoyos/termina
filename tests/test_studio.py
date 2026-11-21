"""Tests of the engine (engine/studio.py) on a talk made in a temporary folder.

They do not need manim: a render is faked with the files a real one leaves.
Run them from the repository root with `uv run pytest`.
"""

import json
import os
import struct
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import zlib
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))
import studio  # noqa: E402


@pytest.fixture
def talk(tmp_path, monkeypatch):
    monkeypatch.setattr(studio, "ROOT", tmp_path)
    monkeypatch.setattr(studio, "REGISTRY", tmp_path / "talks.json")
    monkeypatch.setattr(studio, "REGISTRY_LOCK", tmp_path / ".talks.lock")
    monkeypatch.setattr(studio, "to_recycle_bin", lambda p: p.unlink() or True)
    return studio.new_talk("Docker from scratch", language="en")


def names(talk):
    return [s.name for s in studio.read_plan(talk) if s.active]


def slide(talk, name):
    return next(s for s in studio.read_plan(talk) if s.name == name)


def statuses(talk):
    return {r["name"]: r["status"] for r in studio.talk_status(talk)["slides"]}


def fake_render(talk, *which, quality="1080p"):
    """Leaves what a render leaves: <name>.json, its video and its line in _renders.json."""
    plan = studio.read_plan(talk)
    done = [s for s in plan if s.active and (not which or s.name in which)]
    for s in done:
        video = talk.path(f"files/{s.name}/0.mp4")
        video.parent.mkdir(parents=True, exist_ok=True)
        video.write_bytes(b"video")
        studio.write_json(talk.path(f"{s.name}.json"),
                          {"slides": [{"file": f"diapos\\files\\{s.name}\\0.mp4"}]})
    studio._record(talk, done, studio.shared_fingerprint(talk, plan), quality)


def comment_out(talk, name):
    main = talk.pres / "main.py"
    s = slide(talk, name)
    lines = main.read_text("utf-8").splitlines(keepends=True)
    lines[s.line] = lines[s.line].replace("self.", "# self.", 1)
    main.write_text("".join(lines), "utf-8")


# ───────────────────────────── talks ─────────────────────────────

def test_new_talk(talk):
    assert talk.id == "charla-docker-from-scratch"
    assert names(talk) == ["title", "closing"]
    info = studio.project_info(talk)
    assert (info["title"], info["language"]) == ("Docker from scratch", "en")
    assert "Thank you" in (talk.pres / "diapositivas" / "closing.py").read_text("utf-8")
    assert [t.id for t in studio.talks()] == [talk.id]


def test_new_talk_refuses_bad_input(talk):
    with pytest.raises(RuntimeError, match="language"):
        studio.new_talk("Other", language="spanish")
    with pytest.raises(RuntimeError, match="letter or number"):
        studio.new_talk("¿?")
    with pytest.raises(RuntimeError, match="already a folder"):
        studio.new_talk("Docker from scratch")
    with pytest.raises(RuntimeError, match="folder name"):
        studio.new_talk("Other", folder="con")


def test_new_video_and_reel(talk):
    video = studio.new_talk("Docker from scratch", language="en", kind="video")
    assert video.id == "video-docker-from-scratch"
    assert names(video) == ["title", "end"]
    assert studio.is_video(video) and not studio.vertical(video)
    assert "next_slide" in (video.pres / "diapositivas" / "__init__.py").read_text("utf-8")
    assert not (video.pres / ".manim-slides.toml").exists()
    with pytest.raises(RuntimeError, match="no presenter"):
        studio.present(video)
    reel = studio.new_talk("Docker from scratch", kind="reel")
    assert reel.id == "reel-docker-from-scratch" and studio.vertical(reel)
    with pytest.raises(RuntimeError, match="kind"):
        studio.new_talk("Other", kind="movie")


def test_a_new_shape_renders_again(talk):
    plan = studio.read_plan(talk)
    studio._record(talk, plan[:1], studio.shared_fingerprint(talk, plan), "1080p")
    talk.path(f"{plan[0].name}.json").write_text("{}", "utf-8")  # the status needs it too
    status = lambda: studio.talk_status(talk)["slides"][0]["status"]
    assert status() == "up_to_date"
    studio.save_project(talk, {"kind": "reel"})
    assert status() == "resolution"


def test_chiptune(talk):
    with pytest.raises(RuntimeError, match="a talk has no music"):
        studio.chiptune(talk)
    video = studio.new_talk("Song", kind="video")
    assert "8-bit music" in studio.chiptune(video)
    wav = video.pres / studio.CHIPTUNE_FILE
    assert wav.read_bytes()[:4] == b"RIFF"
    assert studio.project_info(video)["music"] == studio.CHIPTUNE_FILE
    with pytest.raises(RuntimeError, match="music"):
        studio.save_project(video, {"music": "../x.mp3"})


def test_register_gives_unique_ids(talk, tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    first = studio.new_talk("Same", where=tmp_path / "a")
    second = studio.new_talk("Same", where=tmp_path / "b")
    assert (first.id, second.id) == ("charla-same", "charla-same-2")
    assert studio.register(second.pres).id == "charla-same-2"
    assert studio.open_talk(second.pres).id == "charla-same-2"
    studio.forget(first)
    assert "charla-same" not in [t.id for t in studio.talks()]
    assert studio.find_talk("docker-from-scratch").id == talk.id
    with pytest.raises(SystemExit, match="no talk called"):
        studio.find_talk("nope")


def test_save_project(talk):
    (talk.pres / "talk.manimrs").write_text(
        json.dumps({**studio.project_info(talk), "mine": 1}), "utf-8")
    info = studio.save_project(talk, {"title": "  New   title ", "resolution": "720p"})
    assert (info["title"], info["resolution"]) == ("New title", "720p")
    assert json.loads((talk.pres / "talk.manimrs").read_text("utf-8"))["mine"] == 1
    for bad in ({"resolution": "4k"}, {"title": " "}, {"language": "spanish"}, {"colour": "red"}):
        with pytest.raises(RuntimeError):
            studio.save_project(talk, bad)


def test_readme_about():
    lines = ["# Title", "", "> a quote", "First line of **about**", "with [a link](http://x).", "",
             "Second paragraph"]
    assert studio._readme_about(lines) == "First line of about with a link."
    assert studio._readme_about(["# Only a title"]) == ""


def test_migrate_converts_the_spanish_files(talk):
    studio.write_json(talk.path("_registro.json"), {"x": {"metodo": "slide_x", "calidad": "alta"}})
    studio.write_json(talk.path("_revision.json"), {"x": {"estado": "aprobada", "nota": "ok"}})
    studio.write_json(talk.path("_calidades.json"), {"x": "baja"})
    talk.path("_miniaturas").mkdir()
    studio.migrate(talk)
    assert studio.read_json(talk.path("_renders.json"), {})["x"]["quality"] == "1080p"
    assert studio.read_json(talk.path("_reviews.json"), {})["x"]["status"] == "approved"
    assert studio.read_json(talk.path("_resolutions.json"), {}) == {"x": "480p"}
    assert talk.path("_thumbnails").is_dir() and not talk.path("_miniaturas").exists()
    assert not talk.path("_registro.json").exists()


# ───────────────────────────── plan and status ─────────────────────────────

def test_plan_groups_and_repetitions(talk):
    main = talk.pres / "main.py"
    main.write_text(main.read_text("utf-8").replace("        self.slide_title()",
                                                    "        # Part one\n        self.slide_title()"),
                    "utf-8")
    studio.place(talk, "title", slide(talk, "closing"))
    plan = studio.read_plan(talk)
    assert [(s.name, s.pos, s.group) for s in plan] == [
        ("title", 1, "Part one"), ("closing", 2, "Part one"), ("title-2", 3, "Part one")]
    assert (plan[1].previous, plan[2].previous) == ("title", "closing")
    assert studio.file_map(talk.pres)["slide_title"].name == "title.py"


def test_group_starts_renames_and_goes(talk):
    studio.set_group(talk, slide(talk, "closing"), "Part  two")
    assert [s.group for s in studio.read_plan(talk)] == ["", "Part two"]
    studio.set_group(talk, slide(talk, "closing"), "The end")
    assert [s.group for s in studio.read_plan(talk)] == ["", "The end"]
    with pytest.raises(RuntimeError, match="slide call"):
        studio.set_group(talk, slide(talk, "closing"), "self.slide_title()")
    studio.set_group(talk, slide(talk, "closing"), "")
    assert [s.group for s in studio.read_plan(talk)] == ["", ""]
    assert names(talk) == ["title", "closing"]


def test_status_kinds(talk):
    assert statuses(talk) == {"title": "new", "closing": "new"}
    fake_render(talk)
    assert statuses(talk) == {"title": "up_to_date", "closing": "up_to_date"}
    studio.set_resolution(talk, slide(talk, "closing"), "480p")
    assert statuses(talk)["closing"] == "resolution"
    studio.set_resolution(talk, slide(talk, "closing"), None)
    title = talk.pres / "diapositivas" / "title.py"
    title.write_text(title.read_text("utf-8") + "\n", "utf-8")
    assert statuses(talk) == {"title": "changed", "closing": "transition"}
    fake_render(talk)
    (talk.pres / "style.py").write_text("ACCENT = 1\n", "utf-8")
    assert statuses(talk) == {"title": "shared", "closing": "shared"}
    comment_out(talk, "closing")
    assert statuses(talk)["closing"] == "out"


def test_render_at_another_resolution_than_the_talk_is_pending(talk):
    fake_render(talk, quality="480p")
    assert statuses(talk) == {"title": "resolution", "closing": "resolution"}
    studio.save_project(talk, {"resolution": "480p"})
    assert statuses(talk) == {"title": "up_to_date", "closing": "up_to_date"}
    studio.set_resolution(talk, slide(talk, "title"), "1080p")
    assert statuses(talk) == {"title": "resolution", "closing": "up_to_date"}
    pending = [s.name for s in studio.targets_of(talk, studio.read_plan(talk), "pending")]
    assert pending == ["title"]


def test_approval_needs_the_same_code(talk):
    s = slide(talk, "title")
    studio.note(talk, s, None, "approved")
    review = lambda: studio.talk_status(talk)["slides"][0]["review"]["status"]  # noqa: E731
    assert review() == "approved"
    title = talk.pres / "diapositivas" / "title.py"
    title.write_text(title.read_text("utf-8") + "\n", "utf-8")
    assert review() == "to_review"


def test_status_with_media(talk):
    fake_render(talk, "title")
    rows = studio.status_with_media(talk)["slides"]
    assert rows[0]["parts"][0]["url"].startswith(f"/file/{talk.id}/files/title/0.mp4?v=")
    assert rows[1]["parts"] == []


def test_resolve(talk):
    plan = studio.read_plan(talk)
    pick = lambda *texts: [s.name for s in studio.resolve(talk, plan, list(texts))]  # noqa: E731
    assert pick("2", "title", "slide_title", "closing") == ["closing", "title"]
    with pytest.raises(SystemExit, match="did you mean closing"):
        pick("clos")
    with pytest.raises(SystemExit, match="no slide “nope”"):
        pick("nope")
    comment_out(talk, "closing")
    with pytest.raises(SystemExit, match="restore it first"):
        studio.resolve(talk, studio.read_plan(talk), ["closing"])


# ───────────────────────────── editing ─────────────────────────────

def test_edit_import():
    text = "from manim import X\nfrom . import a, c\n\nY = 1\n"
    assert studio._edit_import(text, "", add="b") == "from manim import X\nfrom . import a, b, c\n\nY = 1\n"
    assert studio._edit_import(text, "", remove="a") == "from manim import X\nfrom . import c\n\nY = 1\n"
    assert studio._edit_import(text, "sub", add="z") == (
        "from manim import X\nfrom . import a, c\nfrom .sub import z\n\nY = 1\n")
    one = "from . import a\nY = 1\n"
    assert studio._edit_import(one, "", remove="a") == "Y = 1\n"
    long = [f"name_number_{i}" for i in range(8)]
    out = studio._edit_import(f"from . import {', '.join(long[:-1])}\r\n", "", add=long[-1])
    assert out.startswith("from . import (\r\n    name_number_0,\r\n") and out.endswith(")\r\n")


def test_new_slide(talk):
    s = studio.new_slide(talk, "Git stash, how", slide(talk, "title"))
    assert (s.name, s.pos, s.file) == ("git_stash_how", 2, "diapositivas/git_stash_how.py")
    assert names(talk) == ["title", "git_stash_how", "closing"]
    init = (talk.pres / "diapositivas" / "__init__.py").read_text("utf-8")
    assert "from . import closing, git_stash_how, title" in init
    assert "slide_git_stash_how = _slide(git_stash_how.build)" in init
    assert '"Git stash how"' in (talk.pres / s.file).read_text("utf-8")
    with pytest.raises(RuntimeError, match="already a slide"):
        studio.new_slide(talk, "git stash how", None)


def test_new_slide_keeps_windows_line_endings(talk):
    main = talk.pres / "main.py"
    main.write_bytes(main.read_bytes().replace(b"\n", b"\r\n"))
    studio.new_slide(talk, "Extra", None)
    text = main.read_bytes()
    assert b"self.slide_extra()\r\n" in text and text.count(b"\n") == text.count(b"\r\n")
    assert names(talk) == ["title", "closing", "extra"]


def test_duplicate_copies_the_code_and_goes_after_the_slide(talk):
    studio.new_slide(talk, "volumes", slide(talk, "title"))
    source = talk.pres / "diapositivas" / "volumes.py"
    source.write_text(source.read_text("utf-8") + "# mine", "utf-8")
    copy = studio.duplicate(talk, slide(talk, "volumes"))
    assert names(talk) == ["title", "volumes", "volumes_copy", "closing"]
    assert (talk.pres / copy.file).read_text("utf-8").endswith("# mine")
    assert studio.duplicate(talk, slide(talk, "volumes")).name == "volumes_copy_2"
    assert studio.duplicate(talk, slide(talk, "title"), "Second title").name == "second_title"


def test_export_of_a_video_names_the_videos_in_order(talk, tmp_path):
    fake_render(talk)
    listing = studio._video_list(talk, ["title", "closing"], tmp_path).read_text("utf-8")
    assert [line.rsplit("/", 2)[1] for line in listing.splitlines()] == ["title", "closing"]
    assert "-loop" in studio._video_filter(talk, "gif")
    assert "scale=1920:1080" in studio._video_filter(talk, "mp4")[1]


def test_export_refuses_what_it_cannot_make(talk):
    fake_render(talk, "title")
    with pytest.raises(RuntimeError, match="one slide"):
        studio.export(talk, "gif", log=lambda *_: None)
    with pytest.raises(RuntimeError, match="MP4 or GIF"):
        studio.export(talk, "pdf", log=lambda *_: None, only="title")
    with pytest.raises(RuntimeError, match="not rendered"):
        studio.export(talk, "mp4", log=lambda *_: None, only="closing")


def test_move(talk):
    studio.new_slide(talk, "middle", slide(talk, "title"))
    studio.move(talk, slide(talk, "closing"), None)
    assert names(talk) == ["closing", "title", "middle"]
    studio.move(talk, slide(talk, "closing"), slide(talk, "middle"))
    assert names(talk) == ["title", "middle", "closing"]
    assert studio.move(talk, slide(talk, "title"), slide(talk, "title")) == "It is already there"


def test_rename_keeps_the_renders(talk):
    fake_render(talk)
    title = slide(talk, "title")
    studio.note(talk, title, "bigger", "changes")
    studio.set_resolution(talk, title, "720p")
    studio.rename(talk, title, "Opening")
    assert names(talk) == ["opening", "closing"]
    assert not talk.path("title.json").exists()
    assert talk.path("files/opening/0.mp4").exists()
    files = studio.read_json(talk.path("opening.json"), {})["slides"][0]["file"]
    assert files == "diapos\\files\\opening\\0.mp4"
    renders = studio.read_json(talk.path("_renders.json"), {})
    assert renders["opening"]["method"] == "slide_opening"
    assert renders["closing"]["previous"] == "opening"
    assert studio.read_json(talk.path("_reviews.json"), {})["opening"]["note"] == "bigger"
    assert studio.read_json(talk.path("_resolutions.json"), {}) == {"opening": "720p"}
    assert statuses(talk) == {"opening": "resolution", "closing": "up_to_date"}
    with pytest.raises(RuntimeError, match="already a slide"):
        studio.rename(talk, slide(talk, "opening"), "closing")


def test_restore(talk):
    comment_out(talk, "closing")
    assert names(talk) == ["title"]
    studio.restore(talk, slide(talk, "closing"))
    assert names(talk) == ["title", "closing"]


def test_hide_keeps_the_renders_for_restore(talk):
    fake_render(talk)
    studio.hide(talk, slide(talk, "closing"))
    assert names(talk) == ["title"]
    assert "already" in studio.hide(talk, slide(talk, "closing"))
    studio.restore(talk, slide(talk, "closing"))
    assert statuses(talk) == {"title": "up_to_date", "closing": "up_to_date"}


def test_hide_a_repetition_moves_the_renders_of_the_next(talk):
    studio.place(talk, "title", slide(talk, "closing"))
    fake_render(talk)
    studio.hide(talk, slide(talk, "title"))
    assert names(talk) == ["closing", "title"]
    assert talk.path("title.json").exists() and not talk.path("title-2.json").exists()


def test_speaker_notes_follow_the_slide_and_go_into_its_render(talk):
    speaker = lambda: {r["name"]: r["speaker"] for r in studio.talk_status(talk)["slides"]}  # noqa: E731
    studio.rename(talk, slide(talk, "title"), "cover")
    assert not (talk.pres / studio.SPEAKER_FILE).exists()
    studio.set_speaker(talk, slide(talk, "cover"), " Say hello\nthen wait ")
    fake_render(talk)
    assert statuses(talk)["cover"] == "up_to_date"
    studio.rename(talk, slide(talk, "cover"), "start")
    assert speaker() == {"start": "Say hello\nthen wait", "closing": ""}
    studio._apply_speaker(talk, ["start", "closing"])
    assert studio.read_json(talk.path("start.json"), {})["slides"][0]["notes"] == "Say hello\nthen wait"
    studio.set_speaker(talk, slide(talk, "start"), "")
    studio._apply_speaker(talk, ["start"])
    assert studio.read_json(talk.path("start.json"), {})["slides"][0]["notes"] == ""
    studio.set_speaker(talk, slide(talk, "closing"), "Bye")
    studio.delete(talk, slide(talk, "closing"))
    assert studio.read_json(talk.pres / studio.SPEAKER_FILE, None) == {}


def test_package_has_the_code_and_the_renders_only(talk):
    import zipfile
    fake_render(talk)
    (talk.pres / ".venv").mkdir()
    (talk.pres / ".venv" / "big.bin").write_bytes(b"x")
    talk.path("_stills/title").mkdir(parents=True)
    talk.path("_stills/title/pause_1.png").write_bytes(b"x")
    file = studio.export(talk, "package", log=lambda *_: None)
    studio.export(talk, "package", log=lambda *_: None)  # the old package does not go into the new one
    with zipfile.ZipFile(file) as z:
        inside = {n.split("/", 1)[1] for n in z.namelist()}
    assert {"main.py", "talk.manimrs", "diapositivas/title.py", "diapos/title.json",
            "diapos/files/title/0.mp4", "diapos/_renders.json"} <= inside
    assert not [n for n in inside if n.startswith((".venv", "diapos/exported", "diapos/_stills"))]


def test_pptx_export_asks_manim_slides_for_the_size_of_the_talk(talk, monkeypatch):
    fake_render(talk)
    calls = []
    monkeypatch.setattr(studio, "_convert", lambda t, cmd, log: (calls.append(cmd), Path(cmd[-4]).write_bytes(b"p")))
    file = studio.export(talk, "pptx", log=lambda *_: None)
    assert file.name == f"{talk.id}.pptx"
    assert calls[0][-3:] == ["--to=pptx", "-cwidth=1920", "-cheight=1080"]


def test_source_shows_the_code_and_refuses_code_with_an_error(talk):
    file = talk.pres / "diapositivas" / "title.py"
    file.write_bytes(file.read_bytes().replace(b"\n", b"\r\n"))
    text = studio.source(talk, slide(talk, "title"))["text"]
    assert "def build(scene):" in text and "\r" not in text
    with pytest.raises(RuntimeError, match="line 1"):
        studio.source(talk, slide(talk, "title"), "def build(:\n")
    studio.source(talk, slide(talk, "title"), text + "# mine\n")
    assert file.read_bytes().endswith(b"# mine\r\n")


def test_find_and_replace_only_in_the_text_of_the_slides(talk):
    file = talk.pres / "diapositivas" / "title.py"
    file.write_text('"""Docker is not here."""\nTITLE = "Docker and docker"\ndocker = f"my {TITLE} Docker"\n', "utf-8")
    studio.set_speaker(talk, slide(talk, "closing"), "Say Docker")
    found = studio.find(talk, "docker", case=True)
    assert [(m["slide"], m["line"], m["notes"]) for m in found["matches"]] == [("title", 2, False)]
    assert len(studio.find(talk, "Docker")["matches"]) == 4 and "Docker and" in file.read_text("utf-8")
    assert studio.find(talk, "Docker", "Podman", case=True, word=True)["replaced"] == 3
    assert file.read_text("utf-8").splitlines()[1:] == ['TITLE = "Podman and docker"',
                                                        'docker = f"my {TITLE} Podman"']
    assert studio.talk_status(talk)["slides"][1]["speaker"] == "Say Podman"
    with pytest.raises(RuntimeError, match="breaks the code"):
        studio.find(talk, "Podman", 'a "quote')
    assert "Podman and" in file.read_text("utf-8")


def pptx(path, pages):
    """A PowerPoint file with the least that the import reads. A page is (title, body, notes)."""
    import zipfile
    ns = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
          'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')
    box = lambda kind, text, extra="": (  # noqa: E731
        f'<p:sp><p:nvSpPr><p:nvPr><p:ph type="{kind}"/></p:nvPr></p:nvSpPr><p:spPr>{extra}</p:spPr>'
        f'<p:txBody><a:p><a:r><a:rPr sz="2400"/><a:t>{text}</a:t></a:r></a:p></p:txBody></p:sp>')
    rels = lambda items: "<Relationships>" + "".join(  # noqa: E731
        f'<Relationship Id="{i}" Type="http://x/{kind}" Target="{target}"/>' for i, kind, target in items
    ) + "</Relationships>"
    place = '<a:xfrm><a:off x="0" y="0"/><a:ext cx="6096000" cy="3429000"/></a:xfrm>'
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("ppt/presentation.xml", f'<p:presentation {ns}><p:sldIdLst>' + "".join(
            f'<p:sldId r:id="r{n}"/>' for n in range(len(pages))
        ) + '</p:sldIdLst><p:sldSz cx="12192000" cy="6858000"/></p:presentation>')
        z.writestr("ppt/_rels/presentation.xml.rels",
                   rels((f"r{n}", "slide", f"slides/slide{n}.xml") for n in range(len(pages))))
        for n, (title, body, notes) in enumerate(pages):
            z.writestr(f"ppt/slides/slide{n}.xml", f'<p:sld {ns}><p:cSld><p:spTree>{box("title", title)}'
                       f'{box("body", body, place)}{box("sldNum", "7")}<p:pic><p:blipFill><a:blip r:embed="p"/>'
                       f'</p:blipFill><p:spPr>{place}</p:spPr></p:pic></p:spTree></p:cSld></p:sld>')
            z.writestr(f"ppt/slides/_rels/slide{n}.xml.rels", rels([
                ("p", "image", "../media/a.png"), ("n", "notesSlide", f"../notesSlides/n{n}.xml")]))
            z.writestr(f"ppt/notesSlides/n{n}.xml", f'<p:notes {ns}>{box("body", notes)}</p:notes>')
        z.writestr("ppt/media/a.png", b"png")


def test_import_pptx_makes_a_slide_for_each_page(talk, tmp_path):
    pptx(tmp_path / "deck.pptx", [("Docker día 1", "What it is", "Say hello"), ("Docker día 1", "More", "")])
    made = studio.import_talk(tmp_path / "deck.pptx", tmp_path, "imported")
    assert made.title == "Docker día 1" and names(made) == ["docker_dia_1", "docker_dia_1_2"]
    code = (made.pres / "diapositivas" / "docker_dia_1.py").read_text("utf-8")
    compile(code, "slide", "exec")
    assert '["What it is", 27, -3.56, 2.0, 7.11]' in code and '["Docker día 1", 27, 0, 3, 12]' in code
    assert '"7"' not in code and '["pptx/page1_1.png", -3.56, 2.0, 7.11]' in code
    assert (made.pres / "pptx" / "page1_1.png").read_bytes() == b"png"
    assert studio.read_json(made.pres / studio.SPEAKER_FILE, {}) == {"docker_dia_1": "Say hello"}
    (tmp_path / "bad.pptx").write_bytes(b"no")
    with pytest.raises(RuntimeError, match="not a PowerPoint"):
        studio.import_talk(tmp_path / "bad.pptx", tmp_path)


def test_pause_notes_go_after_the_notes_of_the_slide(talk):
    fake_render(talk)
    studio.set_speaker(talk, slide(talk, "title"), "Hello")
    studio.set_speaker(talk, slide(talk, "title"), "Then this", pause=1)
    studio.rename(talk, slide(talk, "title"), "cover")
    assert studio.talk_status(talk)["slides"][0]["pause_notes"] == {"1": "Then this"}
    studio._apply_speaker(talk, ["cover"])
    assert studio.read_json(talk.path("cover.json"), {})["slides"][0]["notes"] == "Hello\n\nThen this"
    studio.delete(talk, slide(talk, "cover"))
    assert studio.read_json(talk.pres / studio.SPEAKER_FILE, None) == {}


def test_page_numbers_make_a_moved_slide_pending(talk):
    fake_render(talk)
    studio.save_project(talk, {"numbers": "on"})
    assert statuses(talk) == {"title": "number", "closing": "number"}
    fake_render(talk)
    assert set(statuses(talk).values()) == {"up_to_date"}
    with pytest.raises(RuntimeError, match="on or off"):
        studio.save_project(talk, {"numbers": "yes"})


def test_theme_changes_the_colors_of_the_style(talk):
    assert studio.theme_of(talk) == "dark"
    studio.set_theme(talk, "paper")
    assert studio.theme_of(talk) == "paper" and 'ACCENT = "#b4532a"' in (talk.pres / "style.py").read_text("utf-8")
    (talk.pres / "style.py").write_text("X = 1\n", "utf-8")
    assert studio.theme_of(talk) is None
    with pytest.raises(RuntimeError, match="own code"):
        studio.set_theme(talk, "light")


def test_move_retext_and_insert_change_the_code_of_the_slide(talk):
    studio.new_slide(talk, "ideas", slide(talk, "title"))
    file = talk.pres / "diapositivas" / "ideas.py"
    lines = file.read_text("utf-8").splitlines()
    made = next(i for i, l in enumerate(lines, 1) if l.strip().startswith("title = Text("))
    loop = next(i for i, l in enumerate(lines, 1) if l.strip().startswith("text = Text(point"))
    fake_render(talk)
    shown = [{"kind": "text", "text": "ideas", "at": ["diapositivas/ideas.py", made], "parent": None},
             {"kind": "group", "text": "", "at": None, "parent": None},
             {"kind": "text", "text": "First idea", "at": ["diapositivas/ideas.py", loop], "parent": 1}]
    studio.write_json(talk.path("_objects/ideas.json"), {"pauses": [shown]})
    with pytest.raises(RuntimeError, match="inside other code"):
        studio.move_object(talk, slide(talk, "ideas"), 0, 2, 1, 1)
    studio.move_object(talk, slide(talk, "ideas"), 0, 0, 1.5, -0.25)
    with pytest.raises(RuntimeError, match="Render the slide first"):
        studio.move_object(talk, slide(talk, "ideas"), 0, 0, 1, 1)
    fake_render(talk)
    studio.move_object(talk, slide(talk, "ideas"), 0, 0, 0.5, 0.25)
    code = file.read_text("utf-8")
    assert code.count("# termina") == 1
    assert "    title.shift((2.00, 0.00, 0))  # termina\n    scene.play(FadeIn(title" in code
    studio.retext(talk, slide(talk, "ideas"), "First idea", 'La "primera" idea')
    with pytest.raises(RuntimeError, match="different way"):
        studio.retext(talk, slide(talk, "ideas"), "Not there", "x")
    studio.insert(talk, slide(talk, "ideas"), "sphere", 0, 2, -1.5)
    code = file.read_text("utf-8")
    compile(code, "ideas", "exec")
    assert '"La \\"primera\\" idea"' in code and "Text, VGroup, Sphere\n" in code
    assert ("    added_1 = Sphere(radius=1).move_to((2.00, -1.50, 0))  # termina\n"
            "    scene.play(FadeIn(added_1), run_time=0.4)  # termina\n    scene.next_slide()") in code


def test_import_beamer_makes_a_slide_for_each_frame(talk, tmp_path):
    (tmp_path / "fig.png").write_bytes(b"png")
    (tmp_path / "deck.tex").write_text(r"""
\title{Redes}
\begin{document}
\begin{frame}\titlepage\end{frame}
\begin{frame}{Qué es}  % a comment
  Una \textbf{red} aprende.
  \begin{itemize}
    \item Capas \pause
    \item Pesos
  \end{itemize}
  \[ y = wx + b \]
  \includegraphics[width=3cm]{fig}
  \note{Explicar despacio}
\end{frame}
\end{document}""", "utf-8")
    made = studio.import_talk(tmp_path / "deck.tex", tmp_path, "beamer")
    assert made.title == "Redes" and names(made) == ["redes", "que_es"]
    code = (made.pres / "diapositivas" / "que_es.py").read_text("utf-8")
    compile(code, "slide", "exec")
    assert 'TITLE = "Qué es"' in code
    assert ('STEPS = [[["text", "Una red aprende."], ["item", "Capas"]], [["item", "Pesos"], '
            '["formula", "y = wx + b"], ["picture", "beamer/fig.png"]]]') in code
    assert (made.pres / "beamer" / "fig.png").exists()
    assert studio.read_json(made.pres / studio.SPEAKER_FILE, {}) == {"que_es": "Explicar despacio"}


def test_delete_a_repetition_then_the_slide(talk):
    studio.place(talk, "title", slide(talk, "closing"))
    fake_render(talk)
    assert "other repetitions stay" in studio.delete(talk, slide(talk, "title"))
    assert names(talk) == ["closing", "title"]
    assert talk.path("title.json").exists() and not talk.path("title-2.json").exists()
    assert talk.path("files/title/0.mp4").exists()
    assert "recycle bin" in studio.delete(talk, slide(talk, "title"))
    init = (talk.pres / "diapositivas" / "__init__.py").read_text("utf-8")
    assert "slide_title" not in init and "from . import closing\n" in init
    assert not (talk.pres / "diapositivas" / "title.py").exists()
    assert "title" not in studio.read_json(talk.path("_renders.json"), {})


def test_delete_keeps_a_file_that_another_one_imports(talk):
    studio.new_slide(talk, "helper", None)
    closing = talk.pres / "diapositivas" / "closing.py"
    closing.write_text("from .helper import TITLE\n" + closing.read_text("utf-8"), "utf-8")
    assert studio.delete(talk, slide(talk, "helper")).endswith("was deleted")
    assert (talk.pres / "diapositivas" / "helper.py").exists()


def test_render_lock(talk):
    # A killed render left its lock file, and its process id now belongs to a live process.
    lock = talk.path("_render.lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(str(os.getpid()))
    said = []
    with studio.RenderLock(talk, said.append, "3 slide(s) at 480p"):
        second = threading.Thread(target=lambda: studio.RenderLock(talk, said.append).__enter__().__exit__())
        second.start()
        time.sleep(0.5)
        assert second.is_alive(), "a second render must wait for the first one"
        assert len(said) == 1 and said[0].startswith(
            "Another render of this talk is running (3 slide(s) at 480p since ")
    second.join(5)
    assert not second.is_alive(), "it must start when the first one ends"


def png(width, height):
    """An 8-bit RGB PNG, like the frames that ffmpeg writes. The pixels go in two IDAT chunks."""
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    pixels = zlib.compress(b"".join(b"\0" + b"\x2b\x59\xff" * width for _ in range(height)))
    half = len(pixels) // 2
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", pixels[:half]) + chunk(b"IDAT", pixels[half:]) + chunk(b"IEND", b""))


def test_pdf_has_no_page_for_a_loop_after_a_pause(talk):
    fake_render(talk)
    pause, loop = {"file": "a.mp4"}, {"file": "b.mp4", "loop": True}
    studio.write_json(talk.path("opening.json"), {"slides": [pause, loop, pause]})
    studio.write_json(talk.path("closing.json"), {"slides": [loop, pause]})
    videos = studio.pdf_videos(talk, ["opening", "closing"])
    assert [v.name for v in videos] == ["a.mp4", "a.mp4", "b.mp4", "a.mp4"]


def test_pdf_of_pngs():
    pdf = studio.pdf_of_pngs([png(16, 9), png(32, 18)])
    assert pdf.startswith(b"%PDF-1.4") and pdf.endswith(b"%%EOF\n")
    assert b"/Count 2" in pdf and pdf.count(b"/MediaBox [0 0 960 540]") == 2
    assert zlib.decompress(pdf.split(b"stream\n")[1].split(b"\nendstream")[0]).startswith(b"\0\x2b\x59\xff")
    # The cross-reference table must point at each object, or readers have to repair the file.
    start = int(pdf.rsplit(b"startxref\n", 1)[1].split()[0])
    assert pdf[start:].startswith(b"xref")
    rows = pdf[start:].split(b"\n")[3:3 + 8]  # catalog, pages, and page, image, drawing for each
    for n, row in enumerate(rows, 1):
        assert len(row) == 19 and pdf[int(row[:10]):].startswith(f"{n} 0 obj".encode())
    with pytest.raises(RuntimeError):
        studio.pdf_of_pngs([png(4, 4).replace(b"\x08\x02\0\0\0", b"\x08\x06\0\0\0")])


# ───────────────────────────── command line ─────────────────────────────

def test_command_line(talk, capsys):
    out = lambda *argv: (studio.main(list(argv)), capsys.readouterr().out)[1]  # noqa: E731
    assert "Noted the change for title" in out(talk.id, "note", "title", "make", "it", "bigger")
    assert "make it bigger" in out("docker-from-scratch", "notes")
    assert "title approved" in out(talk.id, "note", "title", "--approve")
    assert "Cleared" in out(talk.id, "note", "title", "--clear")
    assert "title: 720p" in out(talk.id, "resolution", "title", "720p")
    assert "the talk's resolution" in out(talk.id, "resolution", "title", "default")
    assert "closing is now first" in out(talk.id, "move", "closing", "--first")
    assert "now called opening" in out(talk.id, "rename", "title", "Opening")
    assert json.loads(out(talk.id, "new", "Extra", "--after", "opening", "--json"))["pos"] == 3
    assert "Placed slide_extra after extra" in out(talk.id, "place", "slide_extra", "--after", "extra")
    assert "extra-2" in out(talk.id, "list")
    assert json.loads(out(talk.id, "status"))["slides"][0]["name"] == "closing"
    assert json.loads(out(talk.id, "info", "--resolution", "720p", "--json"))["resolution"] == "720p"
    assert json.loads(out("talks", "--json"))[0]["id"] == talk.id
    assert "left the talk" in out(talk.id, "delete", "extra-2")
    assert "file is in the recycle bin" in out(talk.id, "delete", "extra")
    comment_out(talk, "opening")
    assert "back in the talk" in out(talk.id, "restore", "opening")
    for argv, message in (([talk.id, "bogus"], "Unknown command"),
                          ([talk.id, "render"], "what to render"),
                          ([talk.id, "move", "opening"], "Tell me where"),
                          ([talk.id, "info", "--resolution", "4k"], "Error"),
                          (["open", "relative"], "Error")):
        with pytest.raises(SystemExit, match=message):
            studio.main(argv)


def test_command_line_contract_of_the_app(talk, capsys, tmp_path):
    """The exact calls of crates/desktop/termina/src/commands/: their arguments and JSON must not change."""
    def call(*argv):
        studio.main(list(argv))
        return json.loads(capsys.readouterr().out)

    (tmp_path / "elsewhere").mkdir()
    made = call("new-talk", "--json", "--about=What", "--language=en",
                f"--in={tmp_path / 'elsewhere'}", "--folder=my-talk", "--", "My title")
    assert set(made) == {"id", "title", "path"} and made["title"] == "My title"
    assert Path(made["path"]) == tmp_path / "elsewhere" / "my-talk"
    assert call("open", "--json", "--", made["path"])["id"] == made["id"]
    assert [t["id"] for t in call("talks", "--json")] == [talk.id, made["id"]]
    info = call(made["id"], "info", "--json", "--title=Other", "--author=Me")
    assert set(info) == {"id", "path", *studio.PROJECT_FIELDS}
    assert (info["title"], info["author"], info["about"]) == ("Other", "Me", "What")


def test_command_line_talks(talk, capsys, tmp_path):
    studio.main(["new-talk", "Second", "talk", "--language", "es", "--json"])
    made = json.loads(capsys.readouterr().out)
    assert made["id"] == "charla-second-talk"
    assert "Gracias" in (Path(made["path"]) / "diapositivas" / "closing.py").read_text("utf-8")
    studio.main(["open", made["path"], "--json"])
    assert json.loads(capsys.readouterr().out)["id"] == "charla-second-talk"
    studio.main([made["id"], "forget"])
    studio.main(["talks"])
    assert "charla-second-talk" not in capsys.readouterr().out


# ───────────────────────────── web panel ─────────────────────────────

@pytest.fixture
def panel(talk, monkeypatch):
    calls = []
    monkeypatch.setattr(studio, "JOBS", studio.Jobs())
    monkeypatch.setattr(studio, "render", lambda t, targets, q, log, on_start: calls.append(
        ([s.name for s in targets], q)))
    monkeypatch.setattr(studio, "_open_in_editor", lambda p: calls.append(("editor", p.name)))
    monkeypatch.setattr(studio, "_open", lambda p: calls.append(("open", p.name)))
    server = ThreadingHTTPServer(("127.0.0.1", 0), studio.panel_handler())
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}", calls
    server.shutdown()


def get(url, **headers):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as r:
            return r.status, r.headers, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read()


def post(url, data, kind="application/json"):
    request = urllib.request.Request(url, json.dumps(data).encode(), {"Content-Type": kind})
    try:
        with urllib.request.urlopen(request) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def test_panel_serves_ranges(panel):
    base, _ = panel
    size = studio.PANEL.stat().st_size
    assert get(base + "/")[0] == 200
    code, headers, body = get(base + "/", Range="bytes=0-9")
    assert (code, len(body), headers["Content-Range"]) == (206, 10, f"bytes 0-9/{size}")
    assert get(base + "/", Range="bytes=-5")[2] == studio.PANEL.read_bytes()[-5:]
    assert get(base + "/", Range="bytes=5-")[2] == studio.PANEL.read_bytes()[5:]
    assert get(base + "/", Range=f"bytes={size}-")[0] == 416
    assert get(base + "/", Host="evil.example")[0] == 403
    assert get(base + "/", Origin="http://evil.example")[0] == 403


def test_panel_cannot_be_framed(panel):
    base, _ = panel
    for url in (base + "/", base + "/api/talks", base + "/nothing"):
        headers = get(url)[1]
        assert headers["X-Frame-Options"] == "DENY"
        assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
        assert headers["X-Content-Type-Options"] == "nosniff"


def test_panel_api(panel, talk):
    base, calls = panel
    assert json.loads(get(base + "/api/talks")[2]) == [{"id": talk.id, "title": "Docker from scratch"}]
    assert json.loads(get(base + f"/api/status?talk={talk.id}")[2])["slides"][0]["name"] == "title"
    assert get(base + "/api/status?talk=nope")[0] == 404
    talk.renders.mkdir()
    talk.path("note.txt").write_text("hi")
    assert get(base + f"/file/{talk.id}/note.txt")[2] == b"hi"
    assert get(base + f"/file/{talk.id}/..%2Fmain.py")[0] == 404
    assert post(base + "/api/review", {"talk": talk.id, "name": "title", "status": "changes",
                                       "note": "x"}) == (200, {"ok": True})
    assert studio.read_json(talk.path("_reviews.json"), {})["title"]["note"] == "x"
    for what in ("pending", "all", ["closing"]):
        assert post(base + "/api/render", {"talk": talk.id, "what": what})[0] == 200
    assert post(base + "/api/open", {"talk": talk.id, "name": "title"})[0] == 200
    assert post(base + "/api/open", {"talk": talk.id, "what": "exported"})[0] == 200
    assert post(base + "/api/cancel", {"id": 99}) == (200, {"ok": True})
    assert post(base + "/api/nothing", {"talk": talk.id})[0] == 400
    assert post(base + "/api/review", {"talk": talk.id}, kind="text/plain")[0] == 403
    deadline = time.time() + 10
    while time.time() < deadline and len([c for c in calls if isinstance(c[0], list)]) < 3:
        time.sleep(0.05)
    renders = [c for c in calls if isinstance(c[0], list)]
    assert renders == [(["title", "closing"], "1080p"), (["title", "closing"], "1080p"),
                       (["closing"], "1080p")]
    assert ("editor", "title.py") in calls and ("open", "exported") in calls


# ───────────────────────────── start and processes ─────────────────────────────

def test_a_missing_program_is_named(talk):
    with pytest.raises(RuntimeError, match="Could not find no-such-program-here"):
        studio.run(["no-such-program-here", "x"], talk.pres, print)


def test_file_url_is_relative_to_the_renders(talk):
    video = talk.path("files/title/a.mp4")
    video.parent.mkdir(parents=True)
    video.write_bytes(b"x")
    assert studio.file_url(talk, video).startswith(f"/file/{talk.id}/files/title/a.mp4?v=")
    roundabout = talk.pres / "diapositivas" / ".." / "diapos" / "files" / "title" / "a.mp4"
    assert studio.file_url(talk, roundabout).startswith(f"/file/{talk.id}/files/title/a.mp4?v=")


def test_the_panel_modules_are_not_loaded_at_start():
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import studio; "
            "print([m for m in ('http.server', 'zipfile', 'webbrowser') if m in sys.modules])")
    out = subprocess.run([sys.executable, "-c", code, str(Path(studio.__file__).parent)],
                         capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "[]"


# ───────────────────────────── MCP server for any agent ─────────────────────────────

def test_mcp_server_answers_an_agent(talk, monkeypatch):
    import mcp_server
    calls = []
    monkeypatch.setattr(mcp_server, "studio", lambda *args: calls.append(args) or "done")
    start = mcp_server.answer({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert start["result"]["serverInfo"]["name"] == "studio"
    assert mcp_server.answer({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
    tools = mcp_server.answer({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]
    assert {t["name"] for t in tools} == {"talks", "slides", "notes", "render", "view", "place",
                                          "export", "new", "chiptune", "present"}
    assert mcp_server.answer({"jsonrpc": "2.0", "id": 3, "method": "nope"})["error"]["code"] == -32601

    def tool(name, **arguments):
        message = {"jsonrpc": "2.0", "id": 9, "method": "tools/call",
                   "params": {"name": name, "arguments": arguments}}
        return mcp_server.answer(message)["result"]

    assert not tool("render", talk="docker", slides=["title", 2], quality="480p")["isError"]
    assert calls[-1] == ("docker", "render", "--quality=480p", "--", "title", "2")
    assert not tool("place", talk="docker", method="slide_x", after="title")["isError"]
    assert calls[-1] == ("docker", "place", "--after=title", "--", "slide_x")
    assert tool("render", talk="docker", slides=[])["isError"]
    assert tool("render", talk="docker", slides=["a"], quality="4k")["isError"]
    assert tool("slides", talk="--help")["isError"]
    assert tool("slides", talk="../other")["isError"]
    assert tool("nothing", talk="docker")["isError"]


def test_mcp_server_over_its_input_and_output(talk):
    server = Path(studio.__file__).with_name("mcp_server.py")
    lines = [{"jsonrpc": "2.0", "id": 1, "method": "ping"}, "not json",
             {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "nothing"}}]
    text = "\n".join(l if isinstance(l, str) else json.dumps(l) for l in lines) + "\n"
    out = subprocess.run([sys.executable, str(server)], input=text, capture_output=True, text=True,
                         encoding="utf-8", check=True)
    first, second, third = (json.loads(l) for l in out.stdout.splitlines())
    assert first == {"jsonrpc": "2.0", "id": 1, "result": {}}
    assert second["error"]["code"] == -32700
    assert third["result"]["isError"]
