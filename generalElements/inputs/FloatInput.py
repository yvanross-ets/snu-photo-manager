import re

from kivy.uix.textinput import TextInput
from kivy.lang.builder import Builder

Builder.load_string("""

<FloatInput>:
    write_tab: False
    background_color: .2, .2, .3, .8
    disabled_foreground_color: 1,1,1,.75
    foreground_color: 1,1,1,1
    size_hint_y: None
    height: app.button_scale
    font_size: app.text_scale
""")

class FloatInput(TextInput):
    pat = re.compile('[^0-9]')

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super(FloatInput, self).insert_text(s, from_undo=from_undo)