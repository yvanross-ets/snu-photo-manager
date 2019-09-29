from kivy.properties import ObjectProperty

from generalElements.dropDowns.NormalDropDown import NormalDropDown
from colorPickerCustom import ColorPickerCustom

from kivy.lang.builder import Builder

Builder.load_string("""
<ColorDropDown>:
    ColorPickerCustom:
        size_hint_y: None
        height: self.parent.width * 1.5
        size_hint_x: 1
        color: root.owner.collage_background
        on_color: root.owner.collage_background = self.color
""")

class ColorDropDown(NormalDropDown):
    owner = ObjectProperty()