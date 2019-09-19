from kivy.properties import ListProperty, BooleanProperty, NumericProperty, StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout

from screenAlbum.customImage import CustomImage
from screenAlbum.CropOverlay import CropOverlay
from screenAlbum.RotateGrid import RotationGrid

from kivy.lang.builder import Builder

Builder.load_string("""
<VideoViewer>:
    SpecialVideoPlayer:
        canvas.after:
            Color:
                rgba: app.theme.favorite if root.favorite else [0, 0, 0, 0]
            Rectangle:
                source: 'data/star.png'
                pos: self.width - (self.width*.03), 44
                size: (self.width*.03, self.width*.03)
        disabled: True if self.opacity == 0 else False
        pos: root.pos
        size: root.size
        id: player
        favorite: root.favorite
        photoinfo: root.photoinfo
        source: root.file
        options: {'allow_stretch': True}
    BoxLayout:
        orientation: 'vertical'
        opacity: 0
        id: overlay
        pos: root.pos
        size: root.size
        RelativeLayout:
            id: photoShow
            height: root.height - 44 - app.button_scale
            width: root.width
            size_hint: None, None
        BoxLayout:
            size_hint: None, None
            height: app.button_scale
            orientation: 'horizontal'
            width: root.width
            NormalButton:
                text: 'Set Start Point'
                on_release: root.set_start_point()
            NormalButton:
                text: 'Clear Start Point'
                warn: True
                on_release: root.reset_start_point()
            Label:
                size_hint_x: 1
            NormalButton:
                text: 'Clear End Point'
                warn: True
                on_release: root.reset_end_point()
            NormalButton:
                text: 'Set End Point'
                on_release: root.set_end_point()
        HalfSliderLimited:
            disabled: True if self.parent.opacity == 0 else False
            size_hint_y: None
            width: root.width
            value: root.position
            start: root.start_point
            end: root.end_point
            on_value: root.position = self.value
            height: app.button_scale

""")


class VideoViewer(FloatLayout):
    """Holds the fullsized video in album view mode."""

    photoinfo = ListProperty()
    favorite = BooleanProperty(False)
    angle = NumericProperty(0)
    mirror = BooleanProperty(False)
    file = StringProperty()
    edit_mode = StringProperty('main')
    bypass = BooleanProperty(False)
    edit_image = ObjectProperty(None, allownone=True)
    position = NumericProperty(0.0)
    start_point = NumericProperty(0.0)
    end_point = NumericProperty(1.0)
    fullscreen = BooleanProperty(False)
    overlay = ObjectProperty(allownone=True)

    def reset_start_point(self, *_):
        self.start_point = 0.0

    def reset_end_point(self, *_):
        self.end_point = 1.0

    def set_start_point(self, *_):
        if self.position < 1.0:
            self.start_point = self.position
            if self.end_point <= self.start_point:
                self.reset_end_point()

    def set_end_point(self, *_):
        if self.position > 0.0:
            self.end_point = self.position
            if self.start_point >= self.end_point:
                self.reset_start_point()

    def on_position(self, *_):
        if self.edit_image:
            self.edit_image.position = self.position

    def on_start_point(self, *_):
        if self.edit_image:
            self.edit_image.start_point = self.start_point

    def on_end_point(self, *_):
        if self.edit_image:
            self.edit_image.end_point = self.end_point

    def on_edit_mode(self, *_):
        """Called when the user enters or exits edit mode.
        Adds the edit image widget, and overlay if need be, and sets them up."""

        overlay_container = self.ids['overlay']
        player = self.ids['player']
        self.position = 0
        self.reset_start_point()
        self.reset_end_point()
        if self.edit_mode == 'main':
            player.opacity = 1
            overlay_container.opacity = 0
            viewer = self.ids['photoShow']
            if self.edit_image:
                self.edit_image.close_video()
                if self.overlay:
                    viewer.remove_widget(self.overlay)
                viewer.remove_widget(self.edit_image)
                self.edit_image = None
        else:
            overlay_container.opacity = 1
            player.opacity = 0
            viewer = self.ids['photoShow']
            self.edit_image = CustomImage(source=self.file, mirror=self.mirror, angle=self.angle, photoinfo=self.photoinfo)
            viewer.add_widget(self.edit_image)
            if self.edit_mode == 'rotate':
                #add rotation grid overlay
                self.overlay = RotationGrid()
                viewer.add_widget(self.overlay)
            if self.edit_mode == 'crop':
                #add cropper overlay and set image to crop mode
                self.overlay = CropOverlay(owner=self.edit_image)
                viewer.add_widget(self.overlay)
                self.edit_image.cropping = True
                self.edit_image.cropper = self.overlay

    def on_fullscreen(self, instance, value):
        player = self.ids['player']
        player.fullscreen = self.fullscreen

    def close(self):
        player = self.ids['player']
        player.close()

    def stop(self):
        """Stops the video playback."""

        player = self.ids['player']
        self.fullscreen = False
        player.state = 'stop'