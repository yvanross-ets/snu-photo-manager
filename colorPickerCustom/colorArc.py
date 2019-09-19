
#__all__ = ('ColorPickerCustom', 'ColorWheel')

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


class _ColorArc(InstructionGroup):
    def __init__(self, r_min, r_max, theta_min, theta_max,
                 color=(0, 0, 1, 1), origin=(0, 0), **kwargs):
        super(_ColorArc, self).__init__(**kwargs)
        self.origin = origin
        self.r_min = r_min
        self.r_max = r_max
        self.theta_min = theta_min
        self.theta_max = theta_max
        self.color = color
        self.color_instr = Color(*color, mode='hsv')
        self.add(self.color_instr)
        self.mesh = self.get_mesh()
        self.add(self.mesh)

    def __str__(self):
        return "r_min: %s r_max: %s theta_min: %s theta_max: %s color: %s" % (
            self.r_min, self.r_max, self.theta_min, self.theta_max, self.color
        )

    def get_mesh(self):
        v = []
        # first calculate the distance between endpoints of the inner
        # arc, so we know how many steps to use when calculating
        # vertices
        end_point_inner = polar_to_rect(
            self.origin, self.r_min, self.theta_max)

        d_inner = d_outer = 3.
        theta_step_inner = (self.theta_max - self.theta_min) / d_inner

        end_point_outer = polar_to_rect(
            self.origin, self.r_max, self.theta_max)

        if self.r_min == 0:
            theta_step_outer = (self.theta_max - self.theta_min) / d_outer
            for x in range(int(d_outer)):
                v += (polar_to_rect(self.origin, 0, 0) * 2)
                v += (polar_to_rect(
                    self.origin, self.r_max,
                    self.theta_min + x * theta_step_outer) * 2)
        else:
            for x in range(int(d_inner + 2)):
                v += (polar_to_rect(
                    self.origin, self.r_min - 1,
                    self.theta_min + x * theta_step_inner) * 2)
                v += (polar_to_rect(
                    self.origin, self.r_max + 1,
                    self.theta_min + x * theta_step_inner) * 2)

        v += (end_point_inner * 2)
        v += (end_point_outer * 2)

        return Mesh(vertices=v, indices=range(int(len(v) / 4)),
                    mode='triangle_strip')

    def change_color(self, color=None, color_delta=None, sv=None, a=None):
        self.remove(self.color_instr)
        if color is not None:
            self.color = color
        elif color_delta is not None:
            self.color = [self.color[i] + color_delta[i] for i in range(4)]
        elif sv is not None:
            self.color = (self.color[0], sv[0], sv[1], self.color[3])
        elif a is not None:
            self.color = (self.color[0], self.color[1], self.color[2], a)
        self.color_instr = Color(*self.color, mode='hsv')
        self.insert(0, self.color_instr)

