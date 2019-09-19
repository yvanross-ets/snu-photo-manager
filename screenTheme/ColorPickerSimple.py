import re

from kivy.properties import ListProperty, StringProperty
from kivy.uix.gridlayout import GridLayout

from generalcommands import hex_to_float, float_to_hex
from kivy.lang.builder import Builder

Builder.load_string("""
<ColorPickerValue@BoxLayout>:
    size_hint_y: None
    height: app.button_scale
    orientation: 'horizontal'
    text: ''
    value: 0
    mroot: None
    NormalLabel:
        text: root.text
        size_hint_x: None
        width: app.button_scale
    NormalInput:
        size_hint_x: None
        width: app.button_scale * 2
        text: format(root.value, '.3f')
    Slider:
        id: sldr
        size_hint: 1, 1
        range: 0, 1
        value: root.value
        on_value:
            root.mroot.update_color(root.text, args[1])
    Widget:
        size_hint_x: None
        width: app.button_scale / 4


<ColorPickerSimple>:
    on_color: app.button_update = not app.button_update
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1
        Rectangle:
            size: root.size
            pos: root.pos
            source: 'data/button.png'
        Color:
            rgba: root.color
        Rectangle:
            size: root.size
            pos: root.pos
            source: 'data/button.png'
    cols: 1
    size_hint_y: None
    height: app.button_scale * 6
    Widget:
        size_hint_y: None
        height: app.button_scale / 2
    ColorPickerValue:
        mroot: root
        text: 'R'
        value: root.color[0]
    ColorPickerValue:
        mroot: root
        text: 'G'
        value: root.color[1]
    ColorPickerValue:
        mroot: root
        text: 'B'
        value: root.color[2]
    ColorPickerValue:
        mroot: root
        text: 'A'
        value: root.color[3]
    BoxLayout:
        orientation: 'horizontal'
        MediumBufferX:
        NormalInput:
            multiline: False
            text: root.hex
            input_filter: root.hex_filter
            on_text: root.on_text(self, self.text)
            on_focus: root.hex_to_color(self.text)
        NormalButton:
            text: 'Set'
        MediumBufferX:
    Widget:
        size_hint_y: None
        height: app.button_scale / 2

""")

class ColorPickerSimple(GridLayout):
    color = ListProperty([1.000, 1.000, 1.000, 1.000])
    hex = StringProperty('00000000')

    def hex_filter(self, value, undo):
        regex = re.compile('[^0123456789ABCDEF]')
        value = regex.sub('', value.upper())
        return value

    def on_text(self, instance, value):
        color = value[:8]
        instance.text = color

    def hex_to_color(self, value):
        self.hex = value

    def on_hex(self, *_):
        color = self.hex.ljust(8, '0')
        r = hex_to_float(color[0:2])
        g = hex_to_float(color[2:4])
        b = hex_to_float(color[4:6])
        a = hex_to_float(color[6:8])
        self.color = [r, g, b, a]

    def on_color(self, *_):
        self.hex = float_to_hex(self.color[0])+float_to_hex(self.color[1])+float_to_hex(self.color[2])+float_to_hex(self.color[3])

    def update_color(self, element, value):
        if element == 'R':
            self.color[0] = round(value, 3)
        elif element == 'G':
            self.color[1] = round(value, 3)
        elif element == 'B':
            self.color[2] = round(value, 3)
        else:
            self.color[3] = round(value, 3)