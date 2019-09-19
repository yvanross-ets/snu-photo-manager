from kivy.animation import Animation
from kivy.app import App
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.splitter import Splitter

from generalElements.SplitterResizer import SplitterResizer

from kivy.lang.builder import Builder

Builder.load_string("""

<SplitterPanel>:
    canvas.before:
        Color:
            rgba: app.theme.sidebar_background
        Rectangle:
            size: self.size
            pos: self.pos
            source: 'data/panelbg.png'
    #keep_within_parent: True
    min_size: int(app.button_scale / 2)
    size_hint: None, 1
    strip_size: int(app.button_scale / 3)
""")
class SplitterPanel(Splitter):
    """Base class for the left and right adjustable panels"""
    hidden = BooleanProperty(False)
    display_width = NumericProperty(0)
    animating = None
    strip_cls = SplitterResizer

    def done_animating(self, *_):
        self.animating = None
        if self.width == 0:
            self.opacity = 0
        else:
            self.opacity = 1

    def on_hidden(self, *_):
        app = App.get_running_app()
        if self.animating:
            self.animating.cancel(self)
        if self.hidden:
            if app.animations:
                self.animating = anim = Animation(width=0, opacity=0, duration=app.animation_length)
                anim.bind(on_complete=self.done_animating)
                anim.start(self)
            else:
                self.opacity = 0
                self.width = 0
        else:
            if app.animations:
                self.animating = anim = Animation(width=self.display_width, opacity=1, duration=app.animation_length)
                anim.bind(on_complete=self.done_animating)
                anim.start(self)
            else:
                self.opacity = 1
                self.width = self.display_width