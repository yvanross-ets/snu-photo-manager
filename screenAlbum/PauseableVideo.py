from kivy.app import App
from kivy.uix.video import Video


class PauseableVideo(Video):
    """modified Video class to allow clicking anywhere to pause/resume."""

    first_load = True

    def on_texture(self, *kwargs):
        super(PauseableVideo, self).on_texture(*kwargs)
        if self.first_load:
            app = App.get_running_app()
            app.album_screen.refresh_photoinfo_full(video=self._video)
        self.first_load = False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.state == 'play':
                self.state = 'pause'
            else:
                self.state = 'play'
            return True