from generalElements.scrollers.Scroller import Scroller


class ScrollerContainer(Scroller):
    def on_touch_down(self, touch):
        #Modified to allow one sub object to not be scrolled
        try:
            subscroller = self.children[0].children[0].ids['wrapper']
            coords = subscroller.window_to_parent(*touch.pos)
            collide = subscroller.collide_point(*coords)
            if collide:
                touch.apply_transform_2d(subscroller.window_to_parent)
                subscroller.on_touch_down(touch)
                return True
        except:
            pass
        super(ScrollerContainer, self).on_touch_down(touch)