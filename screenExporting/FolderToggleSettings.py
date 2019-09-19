from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout

from kivy.lang.builder import Builder

Builder.load_string("""
<FolderToggleSettings>:
    cols: 2
    size_hint_y: None
    height: self.minimum_height
    NormalInput:
        id: exportTo
        input_filter: root.owner.filename_filter
        multiline: False
        text: root.owner.export_folder
        on_focus: root.owner.set_export_folder(self)
    NormalButton:
        text: ' Browse... '
        on_release: root.owner.select_export()
""")

class FolderToggleSettings(GridLayout):
    """Widget layout for the export to folder settings on the export dialog."""
    owner = ObjectProperty()