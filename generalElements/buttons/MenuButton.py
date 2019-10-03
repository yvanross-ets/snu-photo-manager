from generalElements.buttons.ButtonBase import ButtonBase

from kivy.lang.builder import Builder

Builder.load_string("""

<MenuButton>:
    menu: True
    size_hint_x: 1
""")
class MenuButton(ButtonBase):
    """Basic class for a drop-down menu button item."""

    item = None
    # def __init__(self,**kwargs):
    #     super(ButtonBase, self).__init__(**kwargs)
    #     if kwargs is not None:
    #        print(kwargs)
    pass