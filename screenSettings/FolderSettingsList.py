from kivy.uix.recycleview import RecycleView
from kivy.lang.builder import Builder

Builder.load_string("""

<FolderSettingsList>:
    viewclass: 'SimpleRecycleItem'
    SelectableRecycleBoxLayout:
""")

class FolderSettingsList(RecycleView):
    pass