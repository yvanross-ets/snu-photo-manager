from generalElements.DropDown.NormalDropDown import NormalDropDown
from generalElements.Button.MenuButton import MenuButton
from kivy.lang.builder import Builder

Builder.load_string("""

<AlbumSortDropDown>:
    MenuButton:
        id: sort_by_name
        text: 'Name'
        on_release: root.select(self.text)
    MenuButton:
        id: sort_by_path
        text: 'Path'
        on_release: root.select(self.text)
    MenuButton:
        id: sort_by_imported
        text: 'Imported'
        on_release: root.select(self.text)
    MenuButton:
        id: sort_by_modified
        text: 'Modified'
        on_release: root.select(self.text)
""")

class AlbumSortDropDown(NormalDropDown):
    """Drop-down menu for sorting album elements"""
    pass