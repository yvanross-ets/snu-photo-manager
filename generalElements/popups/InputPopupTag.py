from kivy.properties import StringProperty
from kivy.uix.gridlayout import GridLayout

from kivy.lang.builder import Builder

Builder.load_string("""
<InputPopupTag>:
    cols:1
    NormalLabel:
        text: root.text
    NormalInput:
        id: input
        multiline: False
        hint_text: root.hint
        input_filter: app.remove_unallowed_characters
        text: root.input_text
        focus: True
    Label:
    GridLayout:
        cols: 2
        size_hint_y: None
        height: app.button_scale
        WideButton:
            text: 'OK'
            on_release: root.dispatch('on_answer','yes')
        WideButton:
            text: 'Cancel'
            on_release: root.dispatch('on_answer', 'no')
""")
class InputPopupTag(GridLayout):
    """Basic text input popup message.  Calls 'on_answer' when either button is clicked."""

    input_text = StringProperty()
    text = StringProperty()  #Text that the user has input
    hint = StringProperty()  #Grayed-out hint text in the input field

    def __init__(self, **kwargs):
        self.register_event_type('on_answer')
        super(InputPopupTag, self).__init__(**kwargs)

    def on_answer(self, *args):
        pass