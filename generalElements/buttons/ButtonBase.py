from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import BooleanProperty, ListProperty, ObjectProperty
from kivy.uix.button import Button

from kivy.lang.builder import Builder

Builder.load_string("""
<ButtonBase>:
    mipmap: True
    size_hint_y: None
    height: app.button_scale
    background_normal: 'data/button.png'
    background_down: 'data/button.png'
    background_disabled_down: 'data/button.png'
    background_disabled_normal: 'data/button.png'
    button_update: app.button_update
""")
class ButtonBase(Button):
    """Basic button widget."""

    warn = BooleanProperty(False)
    target_background = ListProperty()
    target_text = ListProperty()
    background_animation = ObjectProperty()
    text_animation = ObjectProperty()
    last_disabled = False
    menu = BooleanProperty(False)
    toggle = BooleanProperty(False)

    button_update = BooleanProperty()

    def __init__(self, **kwargs):
        self.background_animation = Animation()
        self.text_animation = Animation()
        app = App.get_running_app()
        self.background_color = app.theme.button_up
        self.target_background = self.background_color
        self.color = app.theme.button_text
        self.target_text = self.color
        super(ButtonBase, self).__init__(**kwargs)

    def on_button_update(self, *_):
        Clock.schedule_once(self.set_color_instant)

    def set_color_instant(self, *_):
        self.set_color(instant=True)


    def set_color(self, instant=False):
        app = App.get_running_app()
        if self.disabled:
            self.set_text(app.theme.button_disabled_text, instant=instant)
            self.set_background(app.theme.button_disabled, instant=instant)
        else:
            self.set_text(app.theme.button_text, instant=instant)
            if self.menu:
                if self.state == 'down':
                    self.set_background(app.theme.button_menu_down, instant=True)
                else:
                    self.set_background(app.theme.button_menu_up, instant=instant)
            elif self.toggle:
                if self.state == 'down':
                    self.set_background(app.theme.button_toggle_true, instant=instant)
                else:
                    self.set_background(app.theme.button_toggle_false, instant=instant)

            elif self.warn:
                if self.state == 'down':
                    self.set_background(app.theme.button_warn_down, instant=True)
                else:
                    self.set_background(app.theme.button_warn_up, instant=instant)
            else:
                if self.state == 'down':
                    self.set_background(app.theme.button_down, instant=True)
                else:
                    self.set_background(app.theme.button_up, instant=instant)

    def on_disabled(self, *_):
        self.set_color()

    def on_menu(self, *_):
        self.set_color(instant=True)

    def on_toggle(self, *_):
        self.set_color(instant=True)

    def on_warn(self, *_):
        self.set_color(instant=True)

    def on_state(self, *_):
        self.set_color()

    def set_background(self, color, instant=False):
        if self.target_background == color:
            return
        app = App.get_running_app()
        self.background_animation.stop(self)
        if app.animations and not instant:
            self.background_animation = Animation(background_color=color, duration=app.animation_length)
            self.background_animation.start(self)
        else:
            self.background_color = color
        self.target_background = color

    def set_text(self, color, instant=False):
        if self.target_text == color:
            return
        app = App.get_running_app()
        self.text_animation.stop(self)
        if app.animations and not instant:
            self.text_animation = Animation(color=color, duration=app.animation_length)
            self.text_animation.start(self)
        else:
            self.color = color
        self.target_text = color