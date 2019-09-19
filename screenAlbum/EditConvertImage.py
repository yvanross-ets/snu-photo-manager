from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout

from kivy.lang.builder import Builder

Builder.load_string("""
<EditConvertImage>:
    cols: 1
    size_hint: 1, None
    height: self.minimum_height
    WideButton:
        text: 'Cancel Edit'
        on_release: root.owner.set_edit_panel('main')
    MediumBufferY:
    NormalLabel:
        text: 'Convert Is Not Available For Images'
""")

class EditConvertImage(GridLayout):
    """Currently not supported."""
    owner = ObjectProperty()

    def refresh_buttons(self):
        pass

    def save_last(self):
        pass

    def load_last(self):
        pass