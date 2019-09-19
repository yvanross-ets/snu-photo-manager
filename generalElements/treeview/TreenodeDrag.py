from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

from kivy.lang.builder import Builder

Builder.load_string("""
<TreenodeDrag>:
    canvas.before:
        Color:
            rgba: (.2, .2, .4, .4)
        Rectangle:
            pos: self.pos
            size: self.size
    orientation: 'vertical'
    size_hint_x: None
    width: 100
    size_hint_y: None
    height: app.button_scale
    NormalLabel:
        text_size: (self.width - 20, None)
        halign: 'left'
        text: root.text
    NormalLabel:
        id: subtext
        text_size: (self.width - 20, None)
        font_size: app.text_scale
        color: .66, .66, .66, 1
        halign: 'left'
        size_hint_y: None
        height: 0
        text: root.subtext
""")
class TreenodeDrag(BoxLayout):
    """Widget that looks like a treenode thumbnail, used for showing the position of the drag-n-drop."""

    fullpath = StringProperty()
    text = StringProperty()
    subtext = StringProperty()