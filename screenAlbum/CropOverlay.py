from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.relativelayout import RelativeLayout

from resizablebehavior import ResizableBehavior
from kivy.lang.builder import Builder

Builder.load_string("""
<CropOverlay>:
    size_hint: None, None
    resizable_left: True
    resizable_right: True
    resizable_up: True
    resizable_down: True
    resize_lock: False
    resizable_border: 40
    resizable_border_offset: 0.5
    RelativeLayout:
        size_hint: 1, 1
        VGridLine:
            pos_hint: {"x": 0.0}
        VGridLine:
            pos_hint: {"x": 0.3333333}
        VGridLine:
            pos_hint: {"x": 0.6666666}
        VGridLine:
            pos_hint: {"x": .999}
    RelativeLayout:
        size_hint: 1, 1
        HGridLine:
            pos_hint: {"y": 0.0}
        HGridLine:
            pos_hint: {"y": 0.3333333}
        HGridLine:
            pos_hint: {"y": 0.6666666}
        HGridLine:
            pos_hint: {"y": .999}
""")

class CropOverlay(ResizableBehavior, RelativeLayout):
    """Overlay widget for showing cropping area."""

    owner = ObjectProperty()
    drag_mode = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(CropOverlay, self).__init__(**kwargs)
        self._drag_touch = None

    def on_mouse_move(self, _, pos):
        """need to override this because the original class will still change mouse cursor after it's removed..."""
        if self.parent:
            super(CropOverlay, self).on_mouse_move(_, pos)

    def on_size(self, instance, size):
        self.owner.set_crop(self.pos[0], self.pos[1], size[0], size[1])

    def on_pos(self, instance, pos):
        self.owner.set_crop(pos[0], pos[1], self.size[0], self.size[1])

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.button == 'left':
                if self.check_resizable_side(*touch.pos):
                    self.drag_mode = False
                    super(CropOverlay, self).on_touch_down(touch)
                else:
                    self.drag_mode = True
            return True

    def on_touch_move(self, touch):
        if self.drag_mode:
            self.x += touch.dx
            self.y += touch.dy

        else:
            super(CropOverlay, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.drag_mode:
            self.drag_mode = False
        else:
            super(CropOverlay, self).on_touch_up(touch)

    def on_resizing(self, instance, resizing):
        pass