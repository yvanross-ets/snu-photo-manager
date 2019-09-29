from kivy.uix.recycleview import RecycleView

from kivy.lang.builder import Builder

Builder.load_string("""

<NormalRecycleView>:
    size_hint: 1, 1
    do_scroll_x: False
    do_scroll_y: True
    scroll_distance: 10
    scroll_timeout: 200
    bar_width: int(app.button_scale * .5)
    bar_color: app.theme.scroller_selected
    bar_inactive_color: app.theme.scroller
    scroll_type: ['bars', 'content']
""")
class NormalRecycleView(RecycleView):
    def get_selected(self):
        selected = []
        for item in self.data:
            if item['selected']:
                selected.append(item)
        return selected