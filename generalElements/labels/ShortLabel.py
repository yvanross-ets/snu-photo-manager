from generalElements.labels.NormalLabel import NormalLabel
from kivy.lang.builder import Builder

Builder.load_string("""
<ShortLabel>:
    mipmap: True
    shorten: True
    shorten_from: 'right'
    font_size: app.text_scale
    size_hint_x: 1
    size_hint_max_x: self.texture_size[0] + 20
    #width: self.texture_size[0] + 20
""")

class ShortLabel(NormalLabel):
    """Label widget that will remain the minimum width"""
    pass