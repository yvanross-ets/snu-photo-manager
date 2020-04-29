from unittest import TestCase
from screens.screenDatabase import ScreenDatabase
from window.Theme import Theme
from kivy.app import App
from kivy.properties import BooleanProperty, NumericProperty, StringProperty, ObjectProperty, ListProperty
from generalElements.buttons.NormalButton import NormalButton
from window.PhotoManager import PhotoManager

class TestScreenDatabase(TestCase):
    def test_update_gps(self):
        app = PhotoManager()
        app.parent = None
        app.canvas = None
        app.load_config()
        app.build()
        app.load_config()
#        app.theme = Theme(self)
#        app.theme.default()
 #       screenDatabase = ScreenDatabase(name='screenDatabase', type='Countries', selected='Countries', displayable=False)
        app.database_screen.update_gps()
        self.fail()
