from generalElements.buttons.ButtonBase import ButtonBase

from kivy.lang.builder import Builder

Builder.load_string("""

<WideButton>:
    text_size: self.size
    halign: 'center'
    valign: 'middle'
""")
class WideButton(ButtonBase):
    """Full width button widget"""
    pass