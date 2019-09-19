from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout

from kivy.lang.builder import Builder

Builder.load_string("""
<ColorElementButton>:
""")
class ColorElementButton(ButtonBehavior, BoxLayout):
    pass