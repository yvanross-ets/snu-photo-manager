from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.lang.builder import Builder

Builder.load_string("""
<AboutPopup>:
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
    size_hint: .5, None
    height: self.width/2
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'horizontal'
            Image:
                source: 'data/icon.png'
                size_hint_x: None
                size_hint_y: 1
                width: self.height
            Scroller:
                do_scroll_x: False
                ShortLabel:
                    size_hint_y: None
                    height: self.texture_size[1] + 20
                    text: app.about_text
        WideButton:
            id: button
            text: root.button_text
            on_release: root.close()
""")

class AboutPopup(Popup):
    """Basic popup message with a message and 'ok' button."""

    button_text = StringProperty('OK')

    def close(self, *_):
        app = App.get_running_app()
        app.popup.dismiss()