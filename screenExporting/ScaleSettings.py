from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout



from kivy.lang.builder import Builder

Builder.load_string("""
<ScaleSettings>:
    canvas.before:
        Color:
            rgba: app.theme.button_down
        BorderImage:
            size: self.size
            pos: self.pos
            source: 'data/tabbg.png'
    padding: app.padding
    spacing: app.padding, app.padding
    cols: 1 if app.simple_interface else 2
    height: self.minimum_height
    size_hint_y: None
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        ShortLabel:
            text: 'Scale To Size:'
        NormalInput:
            input_filter: 'int'
            text: str(root.owner.scale_size)
            on_focus: root.owner.set_scale_size(self)
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        ShortLabel:
            text: 'Scale Size To:'
        MenuStarterButtonWide:
            id: scaleSizeToButton
            size_hint_x: 1
            text: root.owner.scale_size_to_text
            on_release: root.owner.scale_size_to_dropdown.open(self)
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        ShortLabel:
            id: jpegQualityValue
            text: 'Quality: '+str(root.owner.jpeg_quality)+'%'
        NormalSlider:
            size_hint_x: 1
            min: 1
            max: 100
            value: root.owner.jpeg_quality
            on_value: root.owner.set_jpeg_quality(self)
""")

class ScaleSettings(GridLayout):
    """Widget layout for the scale settings on the export dialog."""
    owner = ObjectProperty()