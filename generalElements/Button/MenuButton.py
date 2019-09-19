from generalElements.Button.ButtonBase import ButtonBase

from kivy.lang.builder import Builder

Builder.load_string("""

<MenuButton>:
    menu: True
    size_hint_x: 1
""")
class MenuButton(ButtonBase):
    """Basic class for a drop-down menu button item."""
    pass