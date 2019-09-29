from kivy import platform
from kivy.core.window import Window
from kivy.properties import BooleanProperty
from kivy.uix.recycleview.layout import LayoutSelectionBehavior


class SelectableRecycleLayout(LayoutSelectionBehavior):
    """Custom selectable grid layout widget."""
    multiselect = BooleanProperty(True)

    def __init__(self, **kwargs):
        """ Use the initialize method to bind to the keyboard to enable
        keyboard interaction e.g. using shift and control for multi-select.
        """

        super(SelectableRecycleLayout, self).__init__(**kwargs)
        if str(platform) in ('linux', 'win', 'macosx'):
            keyboard = Window.request_keyboard(None, self)
            keyboard.bind(on_key_down=self.select_with_key_down, on_key_up=self.select_with_key_up)

    def toggle_select(self):
        if self.selected_nodes:
            selected = True
        else:
            selected = False
        self.clear_selection()
        if not selected:
            self.select_all()

    def select_all(self):
        for node in range(0, len(self.parent.data)):
            self.select_node(node)

    def select_with_touch(self, node, touch=None):
        if not self.multiselect:
            self.clear_selection()
        self._shift_down = False
        super(SelectableRecycleLayout, self).select_with_touch(node, touch)

    def _select_range(self, multiselect, keep_anchor, node, idx):
        pass

    def select_range(self, select_index, touch):
        #find the closest selected button

        if self.selected_nodes:
            selected_nodes = self.selected_nodes
        else:
            selected_nodes = [0, len(self.parent.data)]
        closest_node = min(selected_nodes, key=lambda x: abs(x-select_index))

        for index in range(min(select_index, closest_node), max(select_index, closest_node)+1):
            self.select_node(index)