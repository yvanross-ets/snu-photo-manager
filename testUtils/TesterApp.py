from main.Theme import Theme
from tests.utils import data_to_theme
from kivy.properties import NumericProperty
from generalconstants import themes
from kivy.app import App
try:
    from configparser import ConfigParser
except:
    from six.moves import configparser
from screenAlbum.PhotoViewer import PhotoViewer

class TesterApp(App):
    text_scale = 25
    infotext = "Info text"
    animations = 0
    theme = Theme()
    data_to_theme(theme,themes[0])
    button_scale = NumericProperty(25)
    padding = 10
    bubble = ""
    tags = ["allo",'mon','coco']
    config = ConfigParser(interpolation=None)

    def button_update(self):
        pass

    def on_progress(self, widget, pos):
        print("CCCCC on progress")


    def popup_bubble(self, long_press_position, pos):
        self.bubble = long_press_position.text


    def left_panel_width(self):
        return 200