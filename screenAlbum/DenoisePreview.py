from kivy.properties import BooleanProperty
from kivy.uix.relativelayout import RelativeLayout


class DenoisePreview(RelativeLayout):
    finished = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.register_event_type('on_finished')
        super(DenoisePreview, self).__init__(**kwargs)

    def on_finished(self, *_):
        self.root.update_preview()