from kivy.tests.common import GraphicUnitTest, UnitTestTouch
from kivy.base import EventLoop
from kivy.modules import inspector
from kivy.app import App
from kivy.uix.button import Button

from testUtils.TesterApp import TesterApp

class ButtonTestCase(GraphicUnitTest):
    framecount = 0

    def setUp(self):
        self.app = TesterApp()

        EventLoop.ensure_window()
        self._win = EventLoop.window
        self.clean_garbage()

        super(ButtonTestCase, self).setUp()

    def tearDown(self):
        super(ButtonTestCase, self).tearDown()

    def __inspect_node(self,ins):
        for node in ins.treeview.iterate_all_nodes():
            lkey = getattr(node.ids, 'lkey', None)
            if not lkey:
                continue
            print(lkey, lkey.text,  getattr(node.ids, 'ltext', None).text)
            #if lkey.text == 'text':
            #    ltext = node.ids.ltext
                # slice because the string is displayed with quotes
            #    self.assertEqual(ltext.text[1:-1], highlight_exp)
            #    break


    def clean_garbage(self, *args):
        for child in self._win.children[:]:
            self._win.remove_widget(child)
        self.advance_frames(5)

    def test_button_base(self):

        # build the button
        from generalElements.buttons.ButtonBase import ButtonBase
        button = ButtonBase(text="Bonjour", always_release=True)
        self.root = button
        self.render(self.root)

        # activate inspector with root as ctx
        inspector.start(self._win, self.root)
        self.advance_frames(1)

        # pull the Inspector drawer from bottom
        ins = self.root.inspector
        ins.activated = True
        ins.inspect_enabled = True
        self.assertTrue(ins.at_bottom)

         # touch button center
        touch = UnitTestTouch(*self.root.center)
        touch.touch_down()
        touch.touch_up()
        self.assertIsInstance(ins.widget,ButtonBase)

         # check if the button is selected
        self.assertEqual(ins.widget.text, 'Bonjour')

        # self.__inspect_node(ins)

        # close Inspector
        ins.inspect_enabled = False
        ins.activated = False

        # stop Inspector completely
        inspector.stop(self._win, self.root)
        self.assertLess(len(self._win.children), 2)

    def test_explandable_base(self):
        from generalElements.buttons.ExpandableButton import ExpandableButton
        from generalElements.buttons.WideButton import WideButton
        from generalElements.buttons.RemoveButton import RemoveButton
        from kivy.uix.button import Button
        from kivy.uix.checkbox import CheckBox
        print('padding: ', self.app.padding)
        print('padding2:', App.get_running_app().padding)
        button = ExpandableButton()
        self.root = button
        self.render(self.root)

         # activate inspector with root as ctx
        inspector.start(self._win, self.root)
        self.advance_frames(1)

        # pull the Inspector drawer from bottom
        ins = self.root.inspector
        # ins.at_bottom = False
        ins.activated = True
        ins.inspect_enabled = True
        but = Button(text='Move to Top')
        ins.toggle_position(but)
        # self.assertFalse(ins.at_bottom)
        self.advance_frames(5)

         # touch button center
        touch = UnitTestTouch(*self.root.ids.expandable_checkbox.center)
        touch.touch_down()
        touch.touch_up()
        self.assertIsInstance(ins.widget,CheckBox)
        self.advance_frames(2)

        touch = UnitTestTouch(*self.root.ids.expandable_wide_button.center)
        touch.touch_down()
        touch.touch_up()
        self.assertIsInstance(ins.widget,WideButton)
        self.__inspect_node(ins)
        self.advance_frames(2)

        touch = UnitTestTouch(*self.root.ids.expandable_remove_button.center)
        touch.touch_down()
        touch.touch_up()
        self.assertIsInstance(ins.widget,RemoveButton)
        self.advance_frames(2)


        # close Inspector
        ins.inspect_enabled = False
        ins.activated = False

        # stop Inspector completely
        inspector.stop(self._win, self.root)
        self.assertLess(len(self._win.children), 2)
        #self.advance_frames(1)


    def test_normal_button(self):
        from generalElements.buttons.NormalButton import NormalButton

        button = NormalButton(text="Bonjour")
        self.root = button
        self.render(self.root)

         # activate inspector with root as ctx
        inspector.start(self._win, self.root)
        self.advance_frames(1)

        # pull the Inspector drawer from bottom
        ins = self.root.inspector
        ins.activated = True
        ins.inspect_enabled = True

         # touch button center
        touch = UnitTestTouch(*self.root.center)
        touch.touch_down()
        touch.touch_up()
        self.assertIsInstance(ins.widget,NormalButton)
        self.advance_frames(2)

        self.assertEqual(ins.widget.text,'Bonjour')


        # close Inspector
        ins.inspect_enabled = False
        ins.activated = False

        # stop Inspector completely
        inspector.stop(self._win, self.root)
        self.assertLess(len(self._win.children), 2)

    def test_remove_button(self):
        from generalElements.buttons.RemoveButton import RemoveButton

        button = RemoveButton()
        self.root = button
        self.render(self.root)

         # activate inspector with root as ctx
        inspector.start(self._win, self.root)
        self.advance_frames(1)

        # pull the Inspector drawer from bottom
        ins = self.root.inspector
        ins.activated = True
        ins.at_bottom = False
        ins.inspect_enabled = True
        pos = Button(text="Move to Top")
        ins.toggle_position(pos)
        self.assertFalse(ins.at_bottom)
        self.advance_frames(5)

         # touch button center
        touch = UnitTestTouch(*self.root.center)
        touch.touch_down()
        touch.touch_up()
        self.assertIsInstance(ins.widget,RemoveButton)
        self.advance_frames(2)

        self.assertEqual(ins.widget.text,'X')


        # close Inspector
        ins.inspect_enabled = False
        ins.activated = False

        # stop Inspector completely
        inspector.stop(self._win, self.root)
        self.assertLess(len(self._win.children), 2)

    def test_splitterResizer(self):
        from generalElements.buttons.SplitterResizer import SplitterResizer
        self.root =  SplitterResizer()
        self.render(self.root)
        self.advance_frames(1)
        pass

    def test_TootleBase(self):
        from generalElements.buttons.ToogleBase import ToggleBase

        self.root = ToggleBase(text='Bonjour', group='gomp')
        self.render(self.root)

         # activate inspector with root as ctx
        inspector.start(self._win, self.root)
        self.advance_frames(1)

        # pull the Inspector drawer from bottom
        ins = self.root.inspector
        ins.activated = True
        ins.at_bottom = False
        ins.inspect_enabled = True
        pos = Button(text="Move to Top")
        ins.toggle_position(pos)
        self.assertFalse(ins.at_bottom)
        self.advance_frames(5)

         # touch button center
        touch = UnitTestTouch(*self.root.center)
        touch.touch_down()
        touch.touch_up()
        self.assertIsInstance(ins.widget,ToggleBase)
        self.advance_frames(2)

        self.assertEqual(ins.widget.text,'Bonjour')

        # close Inspector
        ins.inspect_enabled = False
        ins.activated = False

        # stop Inspector completely
        inspector.stop(self._win, self.root)
        self.assertLess(len(self._win.children), 2)

    def test_Vertical_button(self):
        from generalElements.buttons.VerticalButton import VerticalButton
        from kivy.uix.label import Label

        self.root = VerticalButton(vertical_text="allo", group='gomp')
        self.render(self.root)

         # activate inspector with root as ctx
        inspector.start(self._win, self.root)
        self.advance_frames(1)

        # pull the Inspector drawer from bottom
        ins = self.root.inspector
        ins.activated = True
        ins.at_bottom = False
        ins.inspect_enabled = True
        pos = Button(text="Move to Top")
        ins.toggle_position(pos)
        self.assertFalse(ins.at_bottom)
        self.advance_frames(5)

         # touch button center
        touch = UnitTestTouch(*self.root.center)
        touch.touch_down()
        touch.touch_up()
        self.assertIsInstance(ins.widget,Label)
        self.advance_frames(2)

        self.__inspect_node(ins)
        self.assertEqual(ins.widget.text,'allo')


        # close Inspector
        ins.inspect_enabled = False
        ins.activated = False

        # stop Inspector completely
        inspector.stop(self._win, self.root)
        self.assertLess(len(self._win.children), 2)

    def test_WideButton(self):
        from generalElements.buttons.WideButton import WideButton
        self.root = WideButton(text="allo")
        self.render(self.root)
        #self.advance_frames(1)
        pass
