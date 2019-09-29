from generalElements.buttons.ButtonBase import ButtonBase

from kivy.lang.builder import Builder

Builder.load_string("""

<NormalButton>:
    width: self.texture_size[0] + app.button_scale
    size_hint_x: None
    font_size: app.text_scale
""")
class NormalButton(ButtonBase):
    """Basic button widget."""
    pass