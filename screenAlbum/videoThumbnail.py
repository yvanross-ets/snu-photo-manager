try:
    import numpy
    import cv2
    opencv = True
except:
    opencv = False
from PIL import  ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from kivy.config import Config
Config.window_icon = "data/icon.png"
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty
from kivy.uix.floatlayout import FloatLayout

from kivy.lang.builder import Builder
Builder.load_string("""
<VideoThumbnail>:
    pos_hint: {'x': 0, 'y': 0}
    image_overlay_play: 'atlas://data/images/defaulttheme/player-play-overlay'
    image_loading: 'data/images/image-loading.gif'
    AsyncThumbnail:
        photoinfo: root.photoinfo
        loadfullsize: False
        allow_stretch: True
        mipmap: True
        source: root.source
        color: (.5, .5, .5, 1)
        pos_hint: {'x': 0, 'y': 0}
    Image:
        source: root.image_overlay_play if not root.click_done else root.image_loading
        pos_hint: {'x': 0, 'y': 0}
""")


class VideoThumbnail(FloatLayout):
    source = ObjectProperty(None)
    video = ObjectProperty(None)
    click_done = BooleanProperty(False)
    photoinfo = ListProperty()
    favorite = BooleanProperty(False)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.click_done:
            self.click_done = True
            self.video.state = 'play'
        return True
