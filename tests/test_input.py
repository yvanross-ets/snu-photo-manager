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
# from tests.utils import *
from testUtils.TesterApp import TesterApp


def displayMsg(value):
    print("displayMsg", value)

class TestInput(GraphicUnitTest):
    framecount = 0

    resort_method = displayMsg

    def setUp(self):
        self.app = TesterApp()
        # app.text_scale = 10
        # app.padding = 10

        EventLoop.ensure_window()
        self._win = EventLoop.window
        self.clean_garbage()

        super(TestInput, self).setUp()

    def tearDown(self):
        super(TestInput, self).tearDown()

    def clean_garbage(self, *args):
        for child in self._win.children[:]:
            self._win.remove_widget(child)
        self.advance_frames(5)

    def test_FloadInput(self):
        self.test_txt = "2.aa45"
        from generalElements.inputs.FloatInput import FloatInput
        self.root = FloatInput()
        self.root.bind(text=self.on_text)
        #self.root.insert_text(self.test_txt)
        self.root.text = self.test_txt

        self.render(self.root)
        self.advance_frames(5)
        pass

    def on_text(self, instance, value):
        # Check if text is modified while recreating from lines and lines_flags
        self.assertEqual(instance.text, self.test_txt)



    def test_FloadInput2(self):
        from generalElements.inputs.FloatInput import FloatInput
        ti = FloatInput()
        ti.focus = True
        self.render(ti)
        self.assertTrue(ti.focus)
        self.assertTrue(ti.text_validate_unfocus)
        ti.text = "3456"
        ti.insert_text("3.16AAA6")
        self.assertEqual(ti.text,"34563.166")


    def test_IntegerInput(self):
        from generalElements.inputs.IntegerInput import IntegerInput
        ti = IntegerInput()
        ti.focus = True
        self.render(ti)
        self.assertTrue(ti.focus)
        self.assertTrue(ti.text_validate_unfocus)
        ti.text = "3456"
        ti.insert_text("3.16AAA6")
        self.assertEqual(ti.text,"34563166")

    def test_NormalInput(self):
        from generalElements.inputs.NormalInput import NormalInput
        ti = NormalInput()
        ti.focus = True
        self.render(ti)
        self.assertTrue(ti.focus)
        self.assertTrue(ti.text_validate_unfocus)
        ti.text = "3456"
        ti.insert_text("3.16AAA6")
        self.assertEqual(ti.text,"34563.16AAA6")
        ti.do_long_press()
        self.assertEqual(self.app.bubble, "34563.16AAA6")

        #self.advance_frames(50)




