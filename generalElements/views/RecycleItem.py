from kivy.app import App
from kivy.properties import ListProperty, ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior

from kivy.lang.builder import Builder

Builder.load_string("""

<RecycleItem>:
    canvas.before:
        Color:
            rgba: self.bgcolor
        Rectangle:
            pos: self.pos
            size: self.size
    size_hint_x: 1
    height: app.button_scale
""")

class RecycleItem(RecycleDataViewBehavior, BoxLayout):
    bgcolor = ListProperty([0, 0, 0, 0])
    owner = ObjectProperty()
    text = StringProperty()
    selected = BooleanProperty(False)
    index = None
    data = {}

    def on_selected(self, *_):
        self.set_color()

    def set_color(self):
        app = App.get_running_app()

        if self.selected:
            self.bgcolor = app.theme.selected
        else:
            if self.index % 2 == 0:
                self.bgcolor = app.list_background_even
            else:
                self.bgcolor = app.list_background_odd

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.data = data
        self.set_color()
        return super(RecycleItem, self).refresh_view_attrs(rv, index, data)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected

    def on_touch_down(self, touch):
        if super(RecycleItem, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos):
            self.parent.selected = self.data
            try:
                self.owner.select(self)
            except:
                pass
            return True