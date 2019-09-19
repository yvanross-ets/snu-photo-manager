from generalElements.label.NormalLabel import NormalLabel

from kivy.lang.builder import Builder

Builder.load_string("""

<PhotoThumbLabel>:
    mipmap: True
    valign: 'middle'
    text_size: (self.width-10, self.height)
    size_hint_y: None
    size_hint_x: None
    height: (app.button_scale * 4)
    width: (app.button_scale * 4)
    text: ''
""")
class PhotoThumbLabel(NormalLabel):
    pass