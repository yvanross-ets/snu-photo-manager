from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from kivy.lang.builder import Builder
Builder.load_string("""
<FolderDetails>:
    size_hint_y: None
    height: app.button_scale if app.simple_interface else int(app.button_scale * 2)
    orientation: 'horizontal'
    Header:
        height: app.button_scale if app.simple_interface else (app.button_scale * 2)
        ShortLabel:
            text: 'Title:'
        NormalInput:
            height: app.button_scale if app.simple_interface else (app.button_scale * 2)
            id: folderTitle
            input_filter: app.test_album
            multiline: False
            text: ''
            on_focus: app.new_title(self, root.owner)
        SmallBufferX:
        ShortLabel:
            text: 'Description:'
        NormalInput:
            id: folderDescription
            height: app.button_scale if app.simple_interface else (app.button_scale * 2)
            input_filter: app.test_description
            multiline: True
            text: ''
            on_focus: app.new_description(self, root.owner)

""")


class FolderDetails(BoxLayout):
    """Widget to display information about a folder of photos"""

    owner = ObjectProperty()

