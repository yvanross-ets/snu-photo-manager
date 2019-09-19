from kivy.app import App
from kivy.properties import ListProperty, BooleanProperty, ObjectProperty
from kivy.uix.videoplayer import VideoPlayer

from screenAlbum.videoThumbnail import VideoThumbnail
from generalcommands import isfile2
from screenAlbum.ExitFullScreenButton import ExitFullscreenButton
from screenAlbum.PauseableVideo import PauseableVideo


class SpecialVideoPlayer(VideoPlayer):
    """Custom VideoPlayer class that replaces the default video widget with the 'PauseableVideo' widget."""

    photoinfo = ListProperty()
    mirror = BooleanProperty(False)
    favorite = BooleanProperty(False)
    exit_button = ObjectProperty()
    owner = ObjectProperty()

    def close(self):
        if self._video is not None:
            self._video.unload()
            self._video = None
        self._image = None
        self.container.clear_widgets()

    def _load_thumbnail(self):
        if not self.container:
            return
        self.container.clear_widgets()
        if self.photoinfo:
            self._image = VideoThumbnail(photoinfo=self.photoinfo, source=self.source, favorite=self.favorite, video=self)
            self.container.add_widget(self._image)

    def on_fullscreen(self, instance, value):
        """Auto-play the video when set to fullscreen."""

        if self.fullscreen:
            self.state = 'play'
            self.owner = self.parent
        if self.owner.fullscreen != self.fullscreen:
            self.owner.fullscreen = self.fullscreen
        super(SpecialVideoPlayer, self).on_fullscreen(instance, value)
        window = self.get_parent_window()
        if self.fullscreen:
            self.exit_button = ExitFullscreenButton(owner=self)
            window.add_widget(self.exit_button)
            self.exit_button.pos[1] = 45
        else:
            window.remove_widget(self.exit_button)

    def _do_video_load(self, *largs):
        """this function has been changed to replace the Video object with the special PauseableVideo object.
        Also, checks if auto-play videos are enabled in the settings.
        """

        if isfile2(self.source):
            self._video = PauseableVideo(source=self.source, state=self.state, volume=self.volume, pos_hint={'x': 0, 'y': 0}, **self.options)
            self._video.bind(texture=self._play_started, duration=self.setter('duration'), position=self.setter('position'), volume=self.setter('volume'), state=self._set_state)
            app = App.get_running_app()
            if app.config.getboolean("Settings", "videoautoplay"):
                self._video.state = 'play'

    def on_touch_down(self, touch):
        """Checks if a double-click was detected, switches to fullscreen if it is."""

        if not self.disabled:
            if not self.collide_point(*touch.pos):
                return False
            if touch.is_double_tap and self.allow_fullscreen:
                self.fullscreen = not self.fullscreen
                return True
            return super(SpecialVideoPlayer, self).on_touch_down(touch)