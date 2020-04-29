import unittest
from kivy.tests.common import GraphicUnitTest, UnitTestTouch
from window.Theme import Theme
from screens.ScreenImportPreset import ScreenImportPreset
from kivy.app import App
from window.PhotoManager import PhotoManager
from kivy.config import ConfigParser
from screenSettings.PhotoManagerSettings import PhotoManagerSettings

class TestScreenImportPreset(GraphicUnitTest):
    framecount = 0

    #resort_method = displayMsg

    # def setUp(self):
    #     self.app = TesterApp()
    #     # app.text_scale = 10
    #     # app.padding = 10
    #
    #     EventLoop.ensure_window()
    #     self._win = EventLoop.window
    #     self.clean_garbage()
    #
    #     super(InputTestCase, self).setUp()

    # def tearDown(self):
    #     super(InputTestCase, self).tearDown()
    #
    # def clean_garbage(self, *args):
    #     for child in self._win.children[:]:
    #         self._win.remove_widget(child)
    #     self.advance_frames(5)


# must create dataase before calling this test
    def test_ScreenImportPreset(self):
        # app = PhotoManager(data_directory=".")
        # app.config = ConfigParser(interpolation=None)
        # app.build_config(app.config)
        #
        # app.theme = Theme(app)
        # app.build()
        # app.show_import()
        # self.render(app)
        pass

