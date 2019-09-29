import unittest
from kivy.tests.common import GraphicUnitTest, UnitTestTouch
from kivy.base import EventLoop
from testUtils.TesterApp import TesterApp




def displayMsg(value):
    print("displayMsg", value)

class ImageTestCase(GraphicUnitTest):
    framecount = 0

    resort_method = displayMsg

    def setUp(self):
        self.app = TesterApp()
        EventLoop.ensure_window()
        self._win = EventLoop.window
        self.clean_garbage()
        super(ImageTestCase, self).setUp()

    def tearDown(self):
        super(ImageTestCase, self).tearDown()

    def clean_garbage(self, *args):
        for child in self._win.children[:]:
            self._win.remove_widget(child)
        self.advance_frames(5)

    def test_AsyncThumbnail(self):
        # from generalElements.Image.AsyncThumbnail import AsyncThumbnail
        # self.root = AsyncThumbnail()
        # self.root.load_thumbnail('./photos/IMG_0919.JPG')
        # self.render(self.root)
        # self.advance_frames(500)
        pass

