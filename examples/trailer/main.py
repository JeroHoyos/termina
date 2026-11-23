from manim import ManimColor
from manim_slides import Slide

from slides import SlideBase, TalkSlides
from style import BACKGROUND


class video(TalkSlides, SlideBase, Slide):
    def construct(self):
        self.camera.background_color = ManimColor(BACKGROUND)

        self.slide_logo()
        self.slide_montage()
        self.slide_uses()
        self.slide_one_slide()
        self.slide_app()
        self.slide_guide()
        self.slide_claude()
        self.slide_export()
        self.slide_reels()
        self.slide_end()
