from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.gridlayout import GridLayout

from kivy.lang.builder import Builder

Builder.load_string("""

<MessagePopup>:
    cols:1
    NormalLabel:
        text: root.text
    Label:
    GridLayout:
        cols:1
        size_hint_y: None
        height: app.button_scale
        WideButton:
            id: button
            text: root.button_text
            on_release: root.close()
""")
class MessagePopup(GridLayout):
    """Basic popup message with a message and 'ok' button."""

    button_text = StringProperty('OK')
    text = StringProperty()

    def close(self, *_):
        app = App.get_running_app()
        app.popup.dismiss()