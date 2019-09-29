from kivy.uix.scrollview import ScrollView

from kivy.lang.builder import Builder

Builder.load_string("""

<Scroller>:
    scroll_distance: 10
    scroll_timeout: 200
    bar_width: int(app.button_scale * .5)
    bar_color: app.theme.scroller_selected
    bar_inactive_color: app.theme.scroller
    scroll_type: ['bars', 'content']
""")
class Scroller(ScrollView):
    """Generic scroller container widget."""
    pass