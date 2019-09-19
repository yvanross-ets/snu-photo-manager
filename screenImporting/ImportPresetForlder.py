from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.treeview import TreeViewNode
from kivy.lang.builder import Builder

Builder.load_string("""
<ImportPresetFolder>:
    orientation: 'horizontal'
    size_hint_y: None
    height: app.button_scale
    NormalLabel:
        text: root.folder
    RemoveButton:
        id: importPresetFolderRemove
        on_release: root.remove_folder()
""")

class ImportPresetFolder(ButtonBehavior, BoxLayout, TreeViewNode):
    """TreeView widget to display a folder scanned on the import process."""

    folder = StringProperty()
    index = NumericProperty()
    owner = ObjectProperty()

    def remove_folder(self):
        self.owner.remove_folder(self.index)