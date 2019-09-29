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

from kivy.lang.builder import Builder

Builder.load_string("""
<ColorPickerCustom>:
    canvas.before:
        Color:
            rgba: self.color
        Rectangle:
            pos: self.pos
            size: self.size

    orientation: 'vertical'
    size_hint_y: None
    height: sp(33)*10 if self. orientation == 'vertical' else sp(33)*5
    foreground_color: (1, 1, 1, 1) if self.hsv[2] * wheel.a < .5 else (0, 0, 0, 1)
    wheel: wheel
    BoxLayout:
        orientation: root.orientation
        spacing: '5sp'
        ColorWheel:
            id: wheel
            color: root.color
            on_color: root.color[:3] = args[1][:3]
        GridLayout:
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            canvas:
                Color:
                    rgba: root.color
                Rectangle:
                    size: self.size
                    pos: self.pos

            ColorPickerCustom_Selector:
                mroot: root
                text: 'R'
                clr_idx: 0
                color: wheel.r
                foreground_color: root.foreground_color
                size_hint_y: None
                height: 0
                disabled: True
                opacity: 0

            ColorPickerCustom_Selector:
                mroot: root
                mode: 'hsv'
                text: 'H'
                clr_idx: 0
                color: root.hsv[0]
                foreground_color: root.foreground_color
                size_hint_y: None
                height: app.button_scale

            ColorPickerCustom_Selector:
                mroot: root
                mode: 'hsv'
                text: 'S'
                clr_idx: 1
                color: root.hsv[1]
                foreground_color: root.foreground_color
                size_hint_y: None
                height: app.button_scale

            ColorPickerCustom_Selector:
                mroot: root
                mode: 'hsv'
                text: 'V'
                clr_idx: 2
                color: root.hsv[2]
                foreground_color: root.foreground_color
                size_hint_y: None
                height: app.button_scale
""")

class ColorPickerCustom(BoxLayout):
    '''
    See module documentation.
    '''

    font_name = StringProperty('data/fonts/RobotoMono-Regular.ttf')
    '''Specifies the font used on the ColorPicker.

    :attr:`font_name` is a :class:`~kivy.properties.StringProperty` and
    defaults to 'data/fonts/RobotoMono-Regular.ttf'.
    '''

    color = ListProperty((1, 1, 1, 1))
    '''The :attr:`color` holds the color currently selected in rgba format.

    :attr:`color` is a :class:`~kivy.properties.ListProperty` and defaults to
    (1, 1, 1, 1).
    '''

    hsv = ListProperty((1, 1, 1))
    '''The :attr:`hsv` holds the color currently selected in hsv format.

    :attr:`hsv` is a :class:`~kivy.properties.ListProperty` and defaults to
    (1, 1, 1).
    '''
    def _get_hex(self):
        return get_hex_from_color(self.color)

    def _set_hex(self, value):
        self.color = get_color_from_hex(value)[:4]

    hex_color = AliasProperty(_get_hex, _set_hex, bind=('color', ))
    '''The :attr:`hex_color` holds the currently selected color in hex.

    :attr:`hex_color` is an :class:`~kivy.properties.AliasProperty` and
    defaults to `#ffffffff`.
    '''

    wheel = ObjectProperty(None)
    '''The :attr:`wheel` holds the color wheel.

    :attr:`wheel` is an :class:`~kivy.properties.ObjectProperty` and
    defaults to None.
    '''

    _update_clr_ev = _update_hex_ev = None

    # now used only internally.
    foreground_color = ListProperty((1, 1, 1, 1))

    def on_color(self, instance, value):
        if not self._updating_clr:
            self._updating_clr = True
            self.hsv = rgb_to_hsv(*value[:3])
            self._updating_clr = False

    def on_hsv(self, instance, value):
        if not self._updating_clr:
            self._updating_clr = True
            self.color[:3] = hsv_to_rgb(*value)
            self._updating_clr = False

    def _trigger_update_clr(self, mode, clr_idx, text):
        self._upd_clr_list = mode, clr_idx, text
        ev = self._update_clr_ev
        if ev is None:
            ev = self._update_clr_ev = Clock.create_trigger(self._update_clr)
        ev()

    def _update_clr(self, dt):
        mode, clr_idx, text = self._upd_clr_list
        try:
            text = min(255, max(0, float(text)))
            if mode == 'rgb':
                self.color[clr_idx] = float(text) / 255.
            else:
                self.hsv[clr_idx] = float(text) / 255.
        except ValueError:
            Logger.warning('ColorPicker: invalid value : {}'.format(text))

    def _update_hex(self, dt):
        if len(self._upd_hex_list) != 9:
            return
        self.hex_color = self._upd_hex_list

    def _trigger_update_hex(self, text):
        self._upd_hex_list = text
        ev = self._update_hex_ev
        if ev is None:
            ev = self._update_hex_ev = Clock.create_trigger(self._update_hex)
        ev()

    def __init__(self, **kwargs):
        self._updating_clr = False
        super(ColorPickerCustom, self).__init__(**kwargs)

