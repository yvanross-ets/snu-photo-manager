from kivy.animation import Animation
from kivy.app import App
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, NumericProperty
from kivy.uix.gridlayout import GridLayout

from kivy.lang.builder import Builder
from generalElements.Button.RemoveButton import RemoveButton
from generalElements.Button.WideButton import WideButton
Builder.load_string("""


<ExpandableButton>:
    cols: 1
    size_hint: 1, None
    height: self.minimum_height
    GridLayout:
        cols: 3
        size_hint: 1, None
        height: app.button_scale
        CheckBox:
            id: expandable_checkbox
            active: root.expanded
            size_hint: None, None
            height: app.button_scale
            width: app.button_scale
            background_checkbox_normal: 'data/tree_closed.png'
            background_checkbox_down: 'data/tree_opened.png'
            on_press: root.set_expanded(self.active)
        WideButton:
            id: expandable_wide_button
            on_press: root.dispatch('on_press')
            on_release: root.dispatch('on_release')
            text: root.text
        RemoveButton:
            id: expandable_remove_button
            on_release: root.dispatch('on_remove')
    GridLayout:
        canvas.before:
            Color:
                rgba: app.theme.menu_background
            BorderImage:
                pos: self.pos
                size: self.size
                source: 'data/buttonflat.png'
        padding: app.padding
        cols: 1
        size_hint: 1, None
        #height: self.minimum_height
        height: app.padding * 2
        opacity: 0
        id: contentContainer
""")
class ExpandableButton(GridLayout):
    """Base class for a button with a checkbox to enable/disable an extra area.
    It also features an 'x' remove button that calls 'on_remove' when clicked."""

    text = StringProperty()  #Text shown in the main button area
    expanded = BooleanProperty(False)  #Determines if the expanded area is displayed
    content = ObjectProperty()  #Widget to be displayed when expanded is enabled
    index = NumericProperty()  #The button's index in the list - useful for the remove function
    animation = None

    def __init__(self, **kwargs):
        super(ExpandableButton, self).__init__(**kwargs)
        self.register_event_type('on_press')
        self.register_event_type('on_release')
        self.register_event_type('on_expanded')
        self.register_event_type('on_remove')

    def set_expanded(self, expanded):
        self.expanded = expanded

    def on_expanded(self, *_):
        if self.content:
            if self.expanded:
                content_container = self.ids['contentContainer']
                self.animate_expand()
            else:
                self.animate_close()

    def animate_close(self, instant=False, *_):
        app = App.get_running_app()
        content_container = self.ids['contentContainer']
        content_container.unbind(minimum_height=self.set_content_height)
        if app.animations and not instant:
            anim = Animation(height=app.padding * 2, opacity=0, duration=app.animation_length)
            anim.start(content_container)
        else:
            content_container.opacity = 0
            content_container.height = app.padding * 2
        content_container.clear_widgets()

    def animate_expand(self, instant=False, *_):
        content_container = self.ids['contentContainer']
        app = App.get_running_app()
        content_container.add_widget(self.content)
        if app.animations and not instant:
            if self.animation:
                self.animation.cancel(content_container)
            self.animation = Animation(height=(self.content.height + (app.padding * 2)), opacity=1, duration=app.animation_length)
            self.animation.start(content_container)
            self.animation.bind(on_complete=self.finish_expand)
        else:
            self.finish_expand()
            content_container.opacity = 1

    def finish_expand(self, *_):
        self.animation = None
        content_container = self.ids['contentContainer']
        content_container.bind(minimum_height=self.set_content_height)

    def set_content_height(self, *_):
        content_container = self.ids['contentContainer']
        content_container.height = content_container.minimum_height

    def on_press(self):
        pass

    def on_release(self):
        pass

    def on_remove(self):
        pass