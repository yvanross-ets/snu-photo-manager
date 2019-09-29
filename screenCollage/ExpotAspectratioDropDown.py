from kivy.properties import ObjectProperty

from generalElements.dropDowns.NormalDropDown import NormalDropDown
from kivy.lang.builder import Builder

Builder.load_string("""
<ExportAspectRatioDropDown>:
    MenuButton:
        text: '16:9 (Wider)'
        on_release:
            root.owner.aspect = 1.7778
            root.owner.aspect_text = '16:9'
            root.dismiss()
    MenuButton:
        text: '4:3 (Wide)'
        on_release:
            root.owner.aspect = 1.3333
            root.owner.aspect_text = '4:3'
            root.dismiss()
    MenuButton:
        text: '1:1 (Square)'
        on_release:
            root.owner.aspect = 1
            root.owner.aspect_text = '1:1'
            root.dismiss()
    MenuButton:
        text: '3:4 (Tall)'
        on_release:
            root.owner.aspect = 0.75
            root.owner.aspect_text = '3:4'
            root.dismiss()
    MenuButton:
        text: '9:16 (Taller)'
        on_release:
            root.owner.aspect = 0.5625
            root.owner.aspect_text = '9:16'
            root.dismiss()
""")

class ExportAspectRatioDropDown(NormalDropDown):
    owner = ObjectProperty()