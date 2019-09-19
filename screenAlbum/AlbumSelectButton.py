from kivy.properties import ObjectProperty, StringProperty
from generalElements.WideButton import WideButton
from kivy.lang.builder import Builder

Builder.load_string("""
<AlbumSelectButton>:
    mipmap: True
    size_hint_x: 1
""")

class AlbumSelectButton(WideButton):
    """Album display button - used for adding a photo to an album."""

    remove = False
    target = StringProperty()
    type = StringProperty('None')
    owner = ObjectProperty()

    def on_press(self):
        self.owner.add_to_album(self.target)

