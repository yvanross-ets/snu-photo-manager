from generalElements.dropDowns.NormalDropDown import NormalDropDown

from kivy.lang.builder import Builder
Builder.load_string("""
<DatabaseSortDropDown>:
    MenuButton:
        text: 'Name'
        on_release: root.select(self.text)
    MenuButton:
        text: 'Title'
        on_release: root.select(self.text)
    MenuButton:
        text: 'Imported'
        on_release: root.select(self.text)
    MenuButton:
        text: 'Modified'
        on_release: root.select(self.text)
    MenuButton:
        text: 'Amount'
        on_release: root.select(self.text)

""")
class DatabaseSortDropDown(NormalDropDown):
    """Drop-down menu for screenDatabase folder sorting"""
    pass
