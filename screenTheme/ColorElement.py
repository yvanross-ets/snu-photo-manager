from kivy.app import App
from kivy.properties import ListProperty, StringProperty, BooleanProperty
from kivy.uix.gridlayout import GridLayout

from screenTheme.ColorPickerSimple import ColorPickerSimple
from screenTheme.ColorElementbutton import ColorElementButton
from kivy.lang.builder import Builder

Builder.load_string("""
<ColorElement>:
    size_hint_y: None
    cols: 1
    height: self.minimum_height
    orientation: 'vertical'
    ColorElementButton:
        on_press: root.toggle_expanded()
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        NormalLabel:
            text: root.text
        Widget:
            size_hint: 1, 1
            canvas.before:
                Color:
                    rgba: 0, 0, 0, 1
                BorderImage:
                    size: self.size
                    pos: self.pos
                    source: 'data/button.png'
                Color:
                    rgba: root.color
                BorderImage:
                    size: self.size
                    pos: self.pos
                    source: 'data/button.png'
    BoxLayout:
        size_hint_y: None
        height: 0
        id: colorPickerContainer
""")
class ColorElement(GridLayout):
    color = ListProperty([1.000, 1.000, 1.000, 1.000])
    text = StringProperty('')
    expanded = BooleanProperty(False)
    color_property = StringProperty('')

    def on_color_property(self, *_):
        app = App.get_running_app()
        self.color = eval('app.theme.'+self.color_property)

    def toggle_expanded(self, *_):
        self.expanded = not self.expanded
        container = self.ids['colorPickerContainer']
        if self.expanded:
            app = App.get_running_app()
            container.clear_widgets()
            container.height = app.button_scale * 6
            picker = ColorPickerSimple()
            picker.color = self.color
            picker.bind(color=self.setter('color'))
            container.add_widget(picker)
        else:
            container.clear_widgets()
            container.height = 0

    def on_color(self, *_):
        app = App.get_running_app()
        setattr(app.theme, self.color_property, self.color)