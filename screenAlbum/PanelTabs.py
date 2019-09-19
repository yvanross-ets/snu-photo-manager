from functools import partial

from kivy.animation import Animation
from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.floatlayout import FloatLayout


class PanelTabs(FloatLayout):
    tab = StringProperty('')
    animate_in = None
    animate_out = None

    def disable_tab(self, tab, *_):
        tab.disabled = True
        tab.size_hint_x = 0

    def on_tab(self, *_):
        app = App.get_running_app()
        animate_in = Animation(opacity=1, duration=app.animation_length)
        animate_out = Animation(opacity=0, duration=app.animation_length)
        for child in self.children:
            if self.animate_in:
                self.animate_in.cancel(child)
            if self.animate_out:
                self.animate_out.cancel(child)
            if child.tab == self.tab:
                child.size_hint_x = 1
                child.disabled = False
                if app.animations:
                    animate_in.start(child)
                else:
                    child.opacity = 1
            else:
                if app.animations:
                    animate_out.start(child)
                    animate_out.bind(on_complete=partial(self.disable_tab, child))
                else:
                    child.opacity = 0
                    child.disabled = True
                    child.size_hint_x = 0
        self.animate_in = animate_in
        self.animate_out = animate_out