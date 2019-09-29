import unittest
from kivy.tests.common import GraphicUnitTest, UnitTestTouch
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.app import App
from kivy.modules import inspector
from kivy.core.window import Window
from main.PhotoManager import PhotoManager
#https://github.com/KeyWeeUsr/KivyUnitTest

class PhotoManagerTestCase(GraphicUnitTest):
    framecount = 0


    def setUp(self):
        self.root = PhotoManager()
        self.root.parent = None
        self.root.canvas = None
        self.root.load_config()
        self.root.build()
        self.root.load_config()
        super(PhotoManagerTestCase, self).setUp()

    def tearDown(self):
        super(PhotoManagerTestCase, self).tearDown()

    def clean_garbage(self, *args):
        for child in self._win.children[:]:
            self._win.remove_widget(child)
        self.advance_frames(5)

    def test_PhotoManager(self):
        inspector.create_inspector(Window,self.root)
        app = App.get_running_app()
        print(app)
        print(self.root)
        Clock.schedule_once(app.stop,5)
        self.root.run()


    def test_show_album(self):

        self.root.show_album()
        #self.advance_frames(500)
        pass

    def test_show_collage(self):

        self.root.show_collage()
        #self.advance_frames(500)
        self.root.stop()
        pass

    def test_show_database(self):

        self.root.show_database()
        self.root.on_stop()
        pass

    def test_show_database_restore(self):
        self.root.load_config()
        self.root.build()
        self.root.load_config()
        self.root.show_database_restore()
        self.root.on_stop()
        pass

    def test_show_export(self):

        self.root.show_export()
        self.root.on_stop()
        pass

    def test_show_import(self):

        self.root.show_import()
        pass

    def test_show_importing(self):

        self.root.show_import()
        self.root.show_importing()
        pass

    def test_show_theme(self):
        self.root.show_theme()
        pass


    def test_show_transfer(self):
        directories = "/Users/rossypro/Downloads;/Users/rossypro/Downloads1"
        self.root.config.set('Database Directories', 'paths',directories)
        self.root.show_transfer()
        pass
