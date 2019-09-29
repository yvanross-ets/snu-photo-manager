from kivy.properties import NumericProperty
from kivy.uix.slider import Slider

from kivy.lang.builder import Builder

Builder.load_string("""
<HalfSliderLimited>:
    #:set sizing 18
    canvas:
        Color:
            rgba: app.theme.slider_background
        BorderImage:
            border: (0, sizing, 0, sizing)
            pos: self.pos
            size: self.size
            source: 'data/sliderbg.png'
        Color:
            rgba: 0, 0, 0, .5
        Rectangle:
            pos: 0, 0
            size: self.width * self.start, self.height
        Rectangle:
            pos: self.width * self.end, 0
            size: self.width * (1 - self.end), self.height
        Color:
            rgba: app.theme.slider_grabber
        Rectangle:
            pos: (self.value_pos[0] - app.button_scale/4, self.center_y - app.button_scale/2)
            size: app.button_scale/2, app.button_scale
            source: 'data/buttonflat.png'
    size_hint_y: None
    height: app.button_scale
    min: 0
    max: 1
    value: 0
""")
class HalfSliderLimited(Slider):
    start = NumericProperty(0.0)
    end = NumericProperty(1.0)