from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout

from kivy.lang.builder import Builder

Builder.load_string("""
<WatermarkSettings>:
    canvas.before:
        Color:
            rgba: app.theme.button_down
        BorderImage:
            size: self.size
            pos: self.pos
            source: 'data/tabbg.png'
    padding: app.padding
    spacing: app.padding, 0
    cols: 3
    size_hint_y: None
    height: self.minimum_height
    GridLayout:
        cols: 1
        size_hint_x: None
        size_hint_y: None
        width: self.minimum_width
        height: app.button_scale * 5
        NormalLabel:
            size_hint_x: None
            width: self.texture_size[0]
            text: 'Image: '
        NormalLabel:
            size_hint_x: None
            width: self.texture_size[0]
            id: watermarkOpacityValue
            text: 'Opacity: '
        NormalLabel:
            size_hint_x: None
            width: self.texture_size[0]
            id: watermarkHorizontalValue
            text: 'Horizontal:'
        NormalLabel:
            size_hint_x: None
            width: self.texture_size[0]
            id: watermarkVerticalValue
            text: 'Vertical: '
        NormalLabel:
            size_hint_x: None
            width: self.texture_size[0]
            id: watermarkSizeValue
            text: 'Size: '

    GridLayout:
        cols: 1
        size_hint_y: None
        height: app.button_scale * 5
        NormalButton:
            size_hint_x: 1
            text: root.owner.watermark_image
            on_release: root.owner.select_watermark()
        NormalSlider:
            size_hint_x: .5
            min: 0
            max: 100
            value: root.owner.watermark_opacity
            on_value: root.owner.set_watermark_opacity(self)
        NormalSlider:
            size_hint_x: .5
            min: 0
            max: 100
            value: root.owner.watermark_horizontal
            on_value: root.owner.set_watermark_horizontal(self)
        NormalSlider:
            size_hint_x: .5
            min: 0
            max: 100
            value: root.owner.watermark_vertical
            on_value: root.owner.set_watermark_vertical(self)
        NormalSlider:
            size_hint_x: .5
            min: 1
            max: 100
            value: root.owner.watermark_size
            on_value: root.owner.set_watermark_size(self)

    StackLayout:
        orientation: 'tb-lr'
        size_hint_x: 0.5
        FloatLayout:
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Rectangle:
                    size: self.size
                    pos: self.pos
                    source: 'data/test.png'
            id: testImage
            size_hint_x: 1
            size_hint_y: None
            height: int(self.width * .75)

""")

class WatermarkSettings(GridLayout):
    """Widget layout for the watermark settings on the export dialog."""
    owner = ObjectProperty()