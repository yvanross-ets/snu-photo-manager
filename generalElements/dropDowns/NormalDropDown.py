from kivy.animation import Animation
from kivy.app import App
from kivy.properties import NumericProperty, BooleanProperty
from kivy.uix.dropdown import DropDown
from kivy.lang.builder import Builder

Builder.load_string("""

<NormalDropDown>:
    canvas.before:
        Color:
            rgba: app.theme.menu_background
        Rectangle:
            size: root.width, root.height * root.show_percent
            pos: root.pos[0], root.pos[1] + (root.height * (1 - root.show_percent)) if root.invert else root.pos[1]
            source: 'data/buttonflat.png'
""")

class NormalDropDown(DropDown):
    """Base dropdown menu class."""

    show_percent = NumericProperty(1)
    invert = BooleanProperty(False)
    basic_animation = BooleanProperty(False)

    def open(self, *args, **kwargs):
        app = App.get_running_app()
        super(NormalDropDown, self).open(*args, **kwargs)

        if app.animations:
            if self.basic_animation:
                #Dont do fancy child opacity animation
                self.opacity = 0
                self.show_percent = 1
                anim = Animation(opacity=1, duration=app.animation_length)
                anim.start(self)
            else:
                #determine if we opened up or down
                if self.attach_to.y > self.y:
                    self.invert = True
                    children = reversed(self.container.children)
                else:
                    self.invert = False
                    children = self.container.children

                #Animate background
                self.opacity = 1
                self.show_percent = 0
                anim = Animation(show_percent=1, duration=app.animation_length)
                anim.start(self)

                if len(self.container.children) > 0:
                    item_delay = app.animation_length / len(self.container.children)
                else:
                    item_delay = 0

                for i, w in enumerate(children):
                    anim = (Animation(duration=i * item_delay) + Animation(opacity=1, duration=app.animation_length))
                    w.opacity = 0
                    anim.start(w)
        else:
            self.opacity = 1

    def dismiss(self, *args, **kwargs):
        app = App.get_running_app()
        if app.animations:
            anim = Animation(opacity=0, duration=app.animation_length)
            anim.start(self)
            anim.bind(on_complete=self.finish_dismiss)
        else:
            self.finish_dismiss()

    def finish_dismiss(self, *_):
        super(NormalDropDown, self).dismiss()