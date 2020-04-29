import unittest
from kivy.tests.common import GraphicUnitTest, UnitTestTouch
from kivy.base import EventLoop
from kivy.modules import inspector
from kivy.factory import Factory
from kivy.app import App
from window.Theme import Theme
from kivy.properties import NumericProperty
from generalconstants import themes
from kivy.uix.button import Button
#from tests.utils import data_to_theme
from testUtils.TesterApp import TesterApp


def displayMsg(value):
    print("displayMsg", value)

class LabelTestCase(GraphicUnitTest):
    framecount = 0

    resort_method = displayMsg

    def setUp(self):
        self.app = TesterApp()
        # app.text_scale = 10
        # app.padding = 10

        EventLoop.ensure_window()
        self._win = EventLoop.window
        self.clean_garbage()

        super(LabelTestCase, self).setUp()

    def tearDown(self):
        super(LabelTestCase, self).tearDown()

    def clean_garbage(self, *args):
        for child in self._win.children[:]:
            self._win.remove_widget(child)
        self.advance_frames(5)

    def test_InfoLabel(self):
        from generalElements.labels.InfoLabel import InfoLabel
        from kivy.properties import ObjectProperty
        label = InfoLabel()
        self.render(label)
        self.advance_frames(1)
        label.stop_blinking()
        self.advance_frames(1)
        self.assertEqual(label.blinker.duration, 4.62)
        label.text = "Allo"
        label.stop_blinking()
        self.assertEqual(label.blinker.duration, 4.62)

    def test_NormalLabel(self):
        from generalElements.labels.NormalLabel import NormalLabel
        label = NormalLabel(text='info')
        self.render(label)
        # self.advance_frames(200)

    def test_PhotoThumbLabel(self):
        from generalElements.labels.PhotoThumbLabel import PhotoThumbLabel
        label = PhotoThumbLabel(text='info')
        self.render(label)
        #self.advance_frames(200)

    def test_ShortLabel(self):
        from generalElements.labels.ShortLabel import ShortLabel
        label = ShortLabel(text='info')
        self.render(label)
        #self.advance_frames(200)


