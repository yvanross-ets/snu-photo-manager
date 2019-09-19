from kivy.properties import ObjectProperty

from generalElements.NormalButton import NormalButton

from kivy.lang.builder import Builder

Builder.load_string("""
<ExitFullscreenButton>:
    text: 'Back'
""")


class ExitFullscreenButton(NormalButton):
    owner = ObjectProperty()

    def on_press(self):
        self.owner.fullscreen = False