from kivy.app import App
from kivy.properties import DictProperty, ListProperty, BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.lang.builder import Builder

Builder.load_string("""

<SelectableRecycleBoxLayout>:
    default_size_hint: 1, None
    default_size: self.width, app.button_scale
    spacing: 2
    size_hint_x: 1
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    multiselect: False
    touch_multiselect: False
""")

class SelectableRecycleBoxLayout(RecycleBoxLayout, LayoutSelectionBehavior):
    """Adds selection and focus behavior to the view."""
    selected = DictProperty()
    selects = ListProperty()
    multiselect = BooleanProperty(False)

    def select_range(self, *_):
        if self.multiselect:
            select_index = self.parent.data.index(self.selected)
            selected_nodes = []
            if self.selects:
                for select in self.selects:
                    selected_nodes.append(self.parent.data.index(select))
            else:
                selected_nodes = [0, len(self.parent.data)]
            closest_node = min(selected_nodes, key=lambda x: abs(x-select_index))

            for index in range(min(select_index, closest_node), max(select_index, closest_node)):
                selected = self.parent.data[index]
                if selected not in self.selects:
                    self.selects.append(selected)
            self.selects.append(self.selected)

    def toggle_select(self, *_):
        if self.multiselect:
            if self.selects:
                self.selects = []
            else:
                all_selects = self.parent.data
                for select in all_selects:
                    self.selects.append(select)
        else:
            if self.selected:
                self.selected = {}
        self.update_selected()

    def check_selected(self):
        temp_selects = []
        for select in self.selects:
            if select in self.parent.data:
                temp_selects.append(select)
        self.selects = temp_selects

    def on_selected(self, *_):
        app = App.get_running_app()
        if self.selected:
            if self.multiselect:
                self.check_selected()
                if self.selected in self.selects:
                    self.selects.remove(self.selected)
                else:
                    if app.shift_pressed:
                        self.select_range()
                    else:
                        self.selects.append(self.selected)
            self.update_selected()

    def on_children(self, *_):
        self.update_selected()

    def update_selected(self):
        for child in self.children:
            if self.multiselect:
                if child.data in self.selects:
                    child.selected = True
                else:
                    child.selected = False
            else:
                if child.data == self.selected:
                    child.selected = True
                else:
                    child.selected = False