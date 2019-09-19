from kivy.animation import Animation
from kivy.app import App
from kivy.uix.gridlayout import GridLayout


class EditPanelContainer(GridLayout):
    panel = None
    animating = None

    def animation_complete(self, *_):
        app = App.get_running_app()
        self.animating = None
        if self.panel:
            self.clear_widgets()
            self.opacity = 0
            self.add_widget(self.panel)
            self.animating = anim = Animation(opacity=1, duration=app.animation_length)
            anim.start(self)

    def change_panel(self, panel):
        app = App.get_running_app()
        self.panel = panel
        if app.animations:
            self.animating = anim = Animation(opacity=0, duration=app.animation_length)
            anim.start(self)
            anim.bind(on_complete=self.animation_complete)
        else:
            self.clear_widgets()
            self.opacity = 1
            if panel:
                self.add_widget(panel)