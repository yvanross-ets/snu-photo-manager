from kivy.uix.label import Label

from kivy.lang.builder import Builder

Builder.load_string("""
<NormalLabel>:
    mipmap: True
    color: app.theme.text
    font_size: app.text_scale
    size_hint_y: None
    height: app.button_scale
""")
class NormalLabel(Label):
    """Basic label widget"""
    pass