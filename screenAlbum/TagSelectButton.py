from kivy.properties import StringProperty, ObjectProperty

from generalElements.buttons.WideButton import WideButton
from kivy.lang.builder import Builder

Builder.load_string("""

<TagSelectButton>:
    mipmap: True
    size_hint_x: 1
""")

class TagSelectButton(WideButton):
    """Tag display button - used for adding a tag to a photo"""

    remove = False
    target = StringProperty()
    type = StringProperty('None')
    owner = ObjectProperty()

    def on_press(self):
        self.owner.add_to_tag(self.target)