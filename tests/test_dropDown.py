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
    animations = 0
    theme = Theme()
    data_to_theme(theme,themes[0])
    button_scale = NumericProperty(25)

    def button_update(self):
        pass

def displayMsg(value):
    print("XXXXXXXXX", value)

class ButtonTestCase(GraphicUnitTest):
    framecount = 0

    resort_method = displayMsg

    def setUp(self):
        app = TesterApp()
        # app.text_scale = 10
        # app.padding = 10

        EventLoop.ensure_window()
        self._win = EventLoop.window
        self.clean_garbage()

        super(ButtonTestCase, self).setUp()

    def tearDown(self):
        super(ButtonTestCase, self).tearDown()

    def clean_garbage(self, *args):
        for child in self._win.children[:]:
            self._win.remove_widget(child)
        self.advance_frames(5)

    def test_NormanDropDown(self):
        from generalElements.DropDown.NormalDropDown import NormalDropDown
        dropDown = NormalDropDown()
        dropDown.add_widget(Button(text="allo"))
        dropDown.add_widget(Button(text="mon"))
        dropDown.add_widget(Button(text="coco"))
        self.root = dropDown
        self.render(self.root)
        self.advance_frames(50)

        pass


    def test_AlbumSortDropDown(self):
        self.advance_frames(100)
        from generalElements.DropDown.AlbumSortDropDown import AlbumSortDropDown
        from generalElements.Button.MenuButton import MenuButton
        dropDown = AlbumSortDropDown()

        self.root = dropDown
        self.render(self.root)
        self.advance_frames(10)

        # activate inspector with root as ctx
        inspector.start(self._win, self.root)
        self.advance_frames(1)

        # pull the Inspector drawer from bottom
        ins = self.root.inspector
        ins.activated = True
        ins.at_bottom = False
        ins.inspect_enabled = True
        self.assertFalse(ins.at_bottom)
        self.advance_frames(5)
        pos = Button(text="Move to Top")
        ins.toggle_position(pos)
        self.advance_frames(50)

        self.render(self.root)
        self.advance_frames(50)

        touch = UnitTestTouch(*self.root.ids.sort_by_name.center)
        touch.touch_down()
        touch.touch_up()
        self.advance_frames(50)
        self.assertIsInstance(ins.widget,MenuButton)
        self.assertEqual(ins.widget.text,'Name')

        touch = UnitTestTouch(*self.root.ids.sort_by_path.center)
        touch.touch_down()
        touch.touch_up()
        #ins.show_widget_info()
        self.assertIsInstance(ins.widget,MenuButton)
        self.assertEqual(ins.widget.text,'Path')
        self.advance_frames(1)

        touch = UnitTestTouch(*self.root.ids.sort_by_imported.center)
        touch.touch_down()
        touch.touch_up()
        self.assertIsInstance(ins.widget,MenuButton)
        self.assertEqual(ins.widget.text,'Imported')
        self.advance_frames(1)

        touch = UnitTestTouch(*self.root.ids.sort_by_modified.center)
        touch.touch_down()
        touch.touch_up()
        self.assertIsInstance(ins.widget,MenuButton)
        self.assertEqual(ins.widget.text,'Modified')
        self.advance_frames(1)

        # close Inspector
        ins.inspect_enabled = False
        ins.activated = False

        # stop Inspector completely
        inspector.stop(self._win, self.root)
        self.assertLess(len(self._win.children), 2)

        pass
