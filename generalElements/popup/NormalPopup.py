from kivy.animation import Animation
from kivy.app import App
from kivy.uix.popup import Popup

from kivy.lang.builder import Builder

Builder.load_string("""
<NormalPopup>:
    canvas.before:
        Color:
            rgba: 0, 0, 0, .75 * self._anim_alpha
        Rectangle:
            size: self._window.size if self._window else (0, 0)
        Color:
            rgba: app.theme.sidebar_background
        Rectangle:
            size: self.size
            pos: self.pos
            source: 'data/panelbg.png'
    background_color: 1, 1, 1, 0
    background: 'data/transparent.png'
    separator_color: 1, 1, 1, .25
    title_size: app.text_scale * 1.25
    title_color: app.theme.header_text
""")
class NormalPopup(Popup):
    """Basic popup widget."""

    def open(self, *args, **kwargs):
        app = App.get_running_app()
        if app.animations:
            self.opacity = 0
            height = self.height
            self.height = 4 * self.height
            anim = Animation(opacity=1, height=height, duration=app.animation_length)
            anim.start(self)
        else:
            self.opacity = 1
        super(NormalPopup, self).open(*args, **kwargs)

    def dismiss(self, *args, **kwargs):
        app = App.get_running_app()
        if app.animations:
            anim = Animation(opacity=0, height=0, duration=app.animation_length)
            anim.start(self)
            anim.bind(on_complete=self.finish_dismiss)
        else:
            super(NormalPopup, self).dismiss()

    def finish_dismiss(self, *_):
        super(NormalPopup, self).dismiss()