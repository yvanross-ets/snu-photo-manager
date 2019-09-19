from generalElements.NormalDropDown import NormalDropDown
from kivy.lang.builder import Builder

Builder.load_string("""
<AspectRatioDropDown>:
    MenuButton:
        text: 'Current Ratio'
        on_release: root.select('current')
    MenuButton:
        text: '6 x 4'
        on_release: root.select('6x4')
    MenuButton:
        text: '7 x 5'
        on_release: root.select('7x5')
    MenuButton:
        text: '11 x 8.5'
        on_release: root.select('11x8.5')
    MenuButton:
        text: '4 x 3'
        on_release: root.select('4x3')
    MenuButton:
        text: '16 x 9'
        on_release: root.select('16x9')
    MenuButton:
        text: '1 x 1'
        on_release: root.select('1x1')
""")

class AspectRatioDropDown(NormalDropDown):
    """Drop-down menu for sorting aspect ratio presets"""
    pass