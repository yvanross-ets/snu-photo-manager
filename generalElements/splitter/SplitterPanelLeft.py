from kivy.app import App
from kivy.core.window import Window

from generalElements.SplitterPanel import SplitterPanel
from kivy.lang.builder import Builder

Builder.load_string("""

<SplitterPanelLeft>:
    width: self.display_width
    disabled: self.hidden
    sizable_from: 'right'
""")

class SplitterPanelLeft(SplitterPanel):
    """Left-side adjustable width panel."""

    def __init__(self, **kwargs):
        app = App.get_running_app()
        self.display_width = app.left_panel_width()
        super(SplitterPanelLeft, self).__init__(**kwargs)

    def on_hidden(self, *_):
        app = App.get_running_app()
        self.display_width = app.left_panel_width()
        super(SplitterPanelLeft, self).on_hidden()

    def on_width(self, instance, width):
        """When the width of the panel is changed, save to the app settings."""

        del instance
        if self.animating:
            return
        if width > 0:
            app = App.get_running_app()
            widthpercent = (width/Window.width)
            app.config.set('Settings', 'leftpanel', widthpercent)
        if self.hidden:
            self.width = 0