from generalElements.RecycleItem import RecycleItem

from kivy.lang.builder import Builder

Builder.load_string("""
<FolderSettingsItem>:
    deselected_color: 0, 0, 0, 1
    selected_color: 0, 0, 1, 1
""")

class FolderSettingsItem(RecycleItem):
    """A Folder item displayed in a folder list popup dialog."""
    pass