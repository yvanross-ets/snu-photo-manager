from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout

from kivy.lang.builder import Builder

Builder.load_string("""

<EditNone>:
    padding: 0, 0, int(app.button_scale / 2), 0
    cols: 1
    size_hint: 1, None
    height: self.minimum_height

""")

class EditNone(GridLayout):
    owner = ObjectProperty()

    def refresh_buttons(self):
        pass

    def save_last(self):
        pass

    def load_last(self):
        pass