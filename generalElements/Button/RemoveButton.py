from kivy.properties import StringProperty, ObjectProperty

from generalElements.Button.ButtonBase import ButtonBase

from kivy.lang.builder import Builder

Builder.load_string("""

<RemoveButton>:
    mipmap: True
    size_hint: None, None
    height: app.button_scale
    width: app.button_scale
    warn: True
    text: 'X'
""")
class RemoveButton(ButtonBase):
    """Base class for a button to remove an item from a list."""

    remove = True
    to_remove = StringProperty()
    remove_from = StringProperty()
    owner = ObjectProperty()