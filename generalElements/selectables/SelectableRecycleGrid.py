from kivy.properties import NumericProperty
from kivy.uix.recyclegridlayout import RecycleGridLayout

from generalElements.selectables.SelectableRecycleLayout import SelectableRecycleLayout

from kivy.lang.builder import Builder

Builder.load_string("""

<SelectableRecycleGrid>:
    cols: max(1, int(self.width / ((app.button_scale * 4 * self.scale) + (app.button_scale / 2))))
    spacing: int(app.button_scale / 2)
    padding: int(app.button_scale / 2)
    focus: False
    touch_multiselect: True
    multiselect: True
    default_size: app.button_scale * 4 * self.scale, app.button_scale * 4 * self.scale
    default_size_hint: None, None
    height: self.minimum_height
    size_hint_y: None
    
""")
class SelectableRecycleGrid(SelectableRecycleLayout, RecycleGridLayout):
    scale = NumericProperty(1)