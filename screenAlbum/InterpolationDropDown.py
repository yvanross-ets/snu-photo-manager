from generalElements.NormalDropDown import NormalDropDown
from kivy.lang.builder import Builder

Builder.load_string("""

<InterpolationDropDown>:
    MenuButton:
        text: 'Linear'
        on_release: root.select('Linear')
    MenuButton:
        text: 'Cosine'
        on_release: root.select('Cosine')
    MenuButton:
        text: 'Cubic'
        on_release: root.select('Cubic')
    MenuButton:
        text: 'Catmull-Rom'
        on_release: root.select('Catmull-Rom')
""")

class InterpolationDropDown(NormalDropDown):
    """Drop-down menu for curves interpolation options"""
    pass