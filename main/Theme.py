from kivy.properties import ListProperty
from kivy.uix.widget import Widget


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