from kivy.graphics.transformation import Matrix
from kivy.properties import BooleanProperty
from kivy.uix.scatterlayout import ScatterLayout


class LimitedScatterLayout(ScatterLayout):
    """Custom ScatterLayout that won't allow sub-widgets to be moved out of the visible area,
    and will not respond to touches outside of the visible area.
    """

    bypass = BooleanProperty(False)

    def on_bypass(self, instance, bypass):
        if bypass:
            self.transform = Matrix()

    def on_transform_with_touch(self, touch):
        """Modified to not allow widgets to be moved out of the visible area."""

        width = self.bbox[1][0]
        height = self.bbox[1][1]
        scale = self.scale

        local_bottom = self.bbox[0][1]
        local_left = self.bbox[0][0]
        local_top = local_bottom+height
        local_right = local_left+width

        local_xmax = width/scale
        local_xmin = 0
        local_ymax = height/scale
        local_ymin = 0

        if local_right < local_xmax:
            self.transform[12] = local_xmin - (width - local_xmax)
        if local_left > local_xmin:
            self.transform[12] = local_xmin
        if local_top < local_ymax:
            self.transform[13] = local_ymin - (height - local_ymax)
        if local_bottom > local_ymin:
            self.transform[13] = local_ymin

    def on_touch_down(self, touch):
        """Modified to only register touches in visible area."""

        if self.bypass:
            for child in self.children[:]:
                if child.dispatch('on_touch_down', touch):
                    return True
        else:
            if self.collide_point(*touch.pos):
                super(LimitedScatterLayout, self).on_touch_down(touch)