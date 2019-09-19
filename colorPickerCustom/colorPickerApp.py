__all__ = ('ColorPickerCustom', 'ColorWheel')

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.properties import (NumericProperty, BoundedNumericProperty,
                             ListProperty, ObjectProperty,
                             ReferenceListProperty, StringProperty,
                             AliasProperty)
from kivy.clock import Clock
from kivy.graphics import Mesh, InstructionGroup, Color
from kivy.utils import get_color_from_hex, get_hex_from_color
from kivy.logger import Logger
from math import cos, sin, pi, sqrt, atan
from colorsys import rgb_to_hsv, hsv_to_rgb
from colorPickerCustom.ColorWheel import ColorWheel
from colorPickerCustom.ColorPickerCustom import ColorPickerCustom

def distance(pt1, pt2):
    return sqrt((pt1[0] - pt2[0]) ** 2. + (pt1[1] - pt2[1]) ** 2.)


def polar_to_rect(origin, r, theta):
    return origin[0] + r * cos(theta), origin[1] + r * sin(theta)


def rect_to_polar(origin, x, y):
    if x == origin[0]:
        if y == origin[1]:
            return (0, 0)
        elif y > origin[1]:
            return (y - origin[1], pi / 2.)
        else:
            return (origin[1] - y, 3 * pi / 2.)
    t = atan(float((y - origin[1])) / (x - origin[0]))
    if x - origin[0] < 0:
        t += pi

    if t < 0:
        t += 2 * pi

    return (distance((x, y), origin), t)


if __name__ in ('__android__', '__main__'):
    from kivy.app import App

    class ColorPickerApp(App):
        def build(self):
            cp = ColorPickerCustom(pos_hint={'center_x': .5, 'center_y': .5},
                             size_hint=(1, 1))
            return cp
    ColorPickerApp().run()
