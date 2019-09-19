import copy

from kivy.app import App
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty, ObjectProperty
from kivy.uix.scatterlayout import ScatterLayout
from kivy.lang.builder import Builder

Builder.load_string("""
<ScatterImage>:
    AsyncThumbnail:
        canvas.after:
            Color:
                rgba: 0, 1, 0, (.2 if root.selected else 0)
            Rectangle:
                size: self.size
                pos: self.pos
        id: image
        size_hint: 1, 1
        photoinfo: root.photoinfo
        mirror: root.mirror
        disable_rotate: True
        #angle: root.image_angle
        loadfullsize: root.loadfullsize
        lowmem: root.lowmem
        source: root.source
""")

class ScatterImage(ScatterLayout):
    source = StringProperty()
    mirror = BooleanProperty(False)
    loadfullsize = BooleanProperty(False)
    image_angle = NumericProperty(0)
    photoinfo = ListProperty()
    fake_touch = ObjectProperty(allownone=True)
    owner = ObjectProperty()
    selected = BooleanProperty(False)
    lowmem = BooleanProperty(False)
    aspect = NumericProperty(1)

    def on_scale(self, *_):
        app = App.get_running_app()
        if (self.width * self.scale) > app.thumbsize:
            self.loadfullsize = True

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.owner.deselect_images()
            self.selected = True
        super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.fake_touch:
            self._touches.remove(self.fake_touch)
            self.fake_touch = None
        super().on_touch_up(touch)

    def transform_with_touch(self, touch):
        if not self.selected:
            return
        right_click = False
        if hasattr(touch, 'button'):
            if touch.button == 'right':
                right_click = True
        if ((not self.do_translation_x and not self.do_translation_y) or right_click) and (self.do_rotation or self.do_scale) and len(self._touches) == 1:
            #Translation is disabled, no need for multitouch to rotate/scale, so if not multitouch, add a new fake touch point to the center of the widget
            self.fake_touch = copy.copy(touch)
            self.fake_touch.pos = self.center
            self._last_touch_pos[self.fake_touch] = self.fake_touch.pos
            self._touches.insert(0, self.fake_touch)
        super().transform_with_touch(touch)