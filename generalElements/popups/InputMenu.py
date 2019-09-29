from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.bubble import Bubble
from kivy.lang.builder import Builder

Builder.load_string("""
<InputMenu>:
    canvas.before:
        Color:
            rgba: app.theme.menu_background
        BorderImage:
            size: self.size
            pos: self.pos
            source: 'data/buttonflat.png'
    size_hint: None, None
    size: app.button_scale * 9, app.button_scale
    show_arrow: False
    MenuButton:
        text: 'Select All'
        on_release: root.select_all()
    MenuButton:
        text: 'Cut'
        on_release: root.cut()
    MenuButton:
        text: 'Copy'
        on_release: root.copy()
    MenuButton:
        text: 'Paste'
        on_release: root.paste()
""")

class InputMenu(Bubble):
    owner = ObjectProperty()

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            app = App.get_running_app()
            app.close_bubble()
        else:
            super(InputMenu, self).on_touch_down(touch)

    def select_all(self, *_):
        if self.owner:
            app = App.get_running_app()
            self.owner.select_all()
            app.close_bubble()

    def cut(self, *_):
        if self.owner:
            app = App.get_running_app()
            self.owner.cut()
            app.close_bubble()

    def copy(self, *_):
        if self.owner:
            app = App.get_running_app()
            self.owner.copy()
            app.close_bubble()

    def paste(self, *_):
        if self.owner:
            app = App.get_running_app()
            self.owner.paste()
            app.close_bubble()