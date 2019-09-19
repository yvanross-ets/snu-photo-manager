from kivy.app import App
from kivy.clock import Clock
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.textinput import TextInput

from kivy.lang.builder import Builder

Builder.load_string("""

<NormalInput>:
    mipmap: True
    cursor_color: app.theme.text
    write_tab: False
    background_color: app.theme.input_background
    hint_text_color: app.theme.disabled_text
    disabled_foreground_color: 1,1,1,.75
    foreground_color: app.theme.text
    size_hint_y: None
    height: app.button_scale
    font_size: app.text_scale
""")
class NormalInput(TextInput):
    messed_up_coords = BooleanProperty(False)
    long_press_time = NumericProperty(1)
    long_press_clock = None
    long_press_pos = None

    def on_touch_up(self, touch):
        if self.long_press_clock:
            self.long_press_clock.cancel()
            self.long_press_clock = None
        super(NormalInput, self).on_touch_up(touch)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            pos = self.to_window(*touch.pos)
            self.long_press_clock = Clock.schedule_once(self.do_long_press, self.long_press_time)
            self.long_press_pos = pos
            if touch.button == 'right':
                app = App.get_running_app()

                app.popup_bubble(self, pos)
                return
        super(NormalInput, self).on_touch_down(touch)

    def do_long_press(self, *_):
        app = App.get_running_app()
        app.popup_bubble(self, self.long_press_pos)