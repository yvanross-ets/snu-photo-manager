from kivy.app import App
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.relativelayout import RelativeLayout


class PhotoShow(ButtonBehavior, RelativeLayout):
    """Widget that holds the image widget.  Used for catching double and tripple clicks."""

    filename = StringProperty()
    fullpath = StringProperty()
    current_touch = None
    bypass = BooleanProperty(False)

    def on_touch_down(self, touch):
        if touch.is_double_tap and not self.bypass:
            app = App.get_running_app()
            if not app.shift_pressed:
                #photowrapper = LimitedScatterLayout()
                photowrapper = self.parent.parent
                #photocontainer = PhotoViewer()
                photocontainer = photowrapper.parent.parent
                if photowrapper.scale > 1:
                    photocontainer.zoom = 0
                    photocontainer.on_zoom()  #Need to call this manually because sometimes it doesnt get called...?
                else:
                    zoompos = self.to_local(touch.pos[0], touch.pos[1])
                    photocontainer.zoompos = zoompos
                    photocontainer.zoom = 1

        else:
            super(PhotoShow, self).on_touch_down(touch)