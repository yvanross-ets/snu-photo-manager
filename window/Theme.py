import json
import os
from kivy.properties import ListProperty
from kivy.uix.widget import Widget
from generalconstants import themes

class Theme(Widget):
    colors = ['button_down', 'button_up', 'button_text', 'button_warn_down', 'button_warn_up', 'button_toggle_true', 'button_toggle_false', 'button_menu_up', 'button_menu_down', 'button_disabled', 'button_disabled_text', 'header_background', 'header_main_background', 'header_text', 'info_text', 'info_background', 'input_background', 'scroller', 'scroller_selected', 'sidebar_background', 'sidebar_resizer', 'slider_grabber', 'slider_background', 'main_background', 'menu_background', 'area_background', 'background', 'text', 'disabled_text', 'selected', 'missing', 'favorite']

    button_down = ListProperty()
    button_up = ListProperty()
    button_text = ListProperty()
    button_warn_down = ListProperty()
    button_warn_up = ListProperty()
    button_toggle_true = ListProperty()
    button_toggle_false = ListProperty()
    button_menu_up = ListProperty()
    button_menu_down = ListProperty()
    button_disabled = ListProperty()
    button_disabled_text = ListProperty()

    header_background = ListProperty()
    header_main_background = ListProperty()
    header_text = ListProperty()

    info_text = ListProperty()
    info_background = ListProperty()

    input_background = ListProperty()

    scroller = ListProperty()
    scroller_selected = ListProperty()

    sidebar_background = ListProperty()
    sidebar_resizer = ListProperty()

    slider_grabber = ListProperty()
    slider_background = ListProperty()

    main_background = ListProperty()
    menu_background = ListProperty()
    area_background = ListProperty()

    background = ListProperty()
    text = ListProperty()
    disabled_text = ListProperty()
    selected = ListProperty()
    missing = ListProperty()
    favorite = ListProperty()

    def __init__(self,app):
        self.app = app


    def default(self):
        data = themes[0]
        self.data_to_theme(data)

        themefile = os.path.realpath(os.path.join(self.app.data_directory, "theme.txt"))
        if themefile and os.path.exists(themefile):
            print('Loading theme file...')
            loaded, data = self.load_theme_data(themefile)
            if loaded:
                self.app.theme.data_to_theme(data)

    def save(self):
        data = self.app.theme_to_data(self)
        themefile = os.path.realpath(os.path.join(self.app.data_directory, "theme.txt"))
        self.save_theme_data(themefile, data)
        self.app.message('Saved Current Theme Settings')

    def theme_to_data(self, theme):
        data = {}
        for color in theme.colors:
            data[color] = list(eval('theme.' + color))
        return data

    def data_to_theme(self, data):
        for color in self.colors:
            try:
                new_color = data[color]
                r = float(new_color[0])
                g = float(new_color[1])
                b = float(new_color[2])
                a = float(new_color[3])
                new_color = [r, g, b, a]
                setattr(self, color, new_color)
            except:
                pass
        self.app.button_update = not self.app.button_update

    def save_theme_data(self, theme_file, data):
        try:
            json.dump(data, open(theme_file, 'w'))
            return True
        except Exception as e:
            return e

    def load_theme_data(self, theme_file):
        try:
            data = json.load(open(theme_file))
            return [True, data]
        except Exception as e:
            return [False, e]