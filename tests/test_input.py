import unittest
from kivy.tests.common import GraphicUnitTest, UnitTestTouch
from kivy.base import EventLoop
from kivy.modules import inspector
from kivy.factory import Factory
from kivy.app import App
from main.Theme import Theme
from kivy.properties import NumericProperty
from generalconstants import themes
from kivy.uix.button import Button

def data_to_theme(theme,data):
    for color in theme.colors:
        try:
            new_color = data[color]
            r = float(new_color[0])
            g = float(new_color[1])
            b = float(new_color[2])
            a = float(new_color[3])
            new_color = [r, g, b, a]
            setattr(theme, color, new_color)
        except:
            pass

class TesterApp(App):
    # button_pressed = False
    text_scale = 15
    animations = 0
    theme = Theme()
    data_to_theme(theme,themes[0])
    button_scale = NumericProperty(25)
    bubble = ""

    def button_update(self):
        pass

    def popup_bubble(self, long_press_position, pos):
        self.bubble = long_press_position.text

def displayMsg(value):
    print("XXXXXXXXX", value)

class InputTestCase(GraphicUnitTest):
    framecount = 0

    resort_method = displayMsg

    def setUp(self):
        self.app = TesterApp()
        # app.text_scale = 10
        # app.padding = 10

        EventLoop.ensure_window()
        self._win = EventLoop.window
        self.clean_garbage()

        super(InputTestCase, self).setUp()

    def tearDown(self):
        super(InputTestCase, self).tearDown()

    def clean_garbage(self, *args):
        for child in self._win.children[:]:
            self._win.remove_widget(child)
        self.advance_frames(5)

    def test_FloadInput(self):
        self.test_txt = "2.aa45"
        from generalElements.input.FloatInput import FloatInput
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
        from generalElements.input.FloatInput import FloatInput
        ti = FloatInput()
        ti.focus = True
        self.render(ti)
        self.assertTrue(ti.focus)
        self.assertTrue(ti.text_validate_unfocus)
        ti.text = "3456"
        ti.insert_text("3.16AAA6")
        self.assertEqual(ti.text,"34563.166")


    def test_IntegerInput(self):
        from generalElements.input.IntegerInput import IntegerInput
        ti = IntegerInput()
        ti.focus = True
        self.render(ti)
        self.assertTrue(ti.focus)
        self.assertTrue(ti.text_validate_unfocus)
        ti.text = "3456"
        ti.insert_text("3.16AAA6")
        self.assertEqual(ti.text,"34563166")

    def test_NormalInput(self):
        from generalElements.input.NormalInput import NormalInput
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




