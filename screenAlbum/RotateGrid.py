from kivy.uix.floatlayout import FloatLayout

from kivy.lang.builder import Builder

Builder.load_string("""
<VGridLine@Widget>:
    canvas.before:
        Color:
            rgba: 1,1,1,.5
        Rectangle:
            pos: self.pos
            size: 1, self.size[1]

<HGridLine@Widget>:
    size_hint: 1, 1
    canvas.before:
        Color:
            rgba: 1,1,1,.5
        Rectangle:
            pos: self.pos
            size: self.size[0], 1

<RotationGrid>:
    RelativeLayout:
        size_hint: 1, 1
        VGridLine:
            pos_hint: {"x": 0.0}
        VGridLine:
            pos_hint: {"x": 0.1}
        VGridLine:
            pos_hint: {"x": 0.2}
        VGridLine:
            pos_hint: {"x": 0.3}
        VGridLine:
            pos_hint: {"x": 0.4}
        VGridLine:
            pos_hint: {"x": 0.5}
        VGridLine:
            pos_hint: {"x": 0.6}
        VGridLine:
            pos_hint: {"x": 0.7}
        VGridLine:
            pos_hint: {"x": 0.8}
        VGridLine:
            pos_hint: {"x": 0.9}
        VGridLine:
            pos_hint: {"x": 1.0}
    RelativeLayout:
        size_hint: 1, 1
        HGridLine:
            pos_hint: {"y": 0.0}
        HGridLine:
            pos_hint: {"y": 0.1}
        HGridLine:
            pos_hint: {"y": 0.2}
        HGridLine:
            pos_hint: {"y": 0.3}
        HGridLine:
            pos_hint: {"y": 0.4}
        HGridLine:
            pos_hint: {"y": 0.5}
        HGridLine:
            pos_hint: {"y": 0.6}
        HGridLine:
            pos_hint: {"y": 0.7}
        HGridLine:
            pos_hint: {"y": 0.8}
        HGridLine:
            pos_hint: {"y": 0.9}
        HGridLine:
            pos_hint: {"y": 1.0}
""")

class RotationGrid(FloatLayout):
    """A grid display overlay used for alignment when an image is being rotated."""
    pass