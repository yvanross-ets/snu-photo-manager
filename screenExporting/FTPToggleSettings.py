from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.lang.builder import Builder

Builder.load_string("""
<FTPToggleSettings>:
    size_hint_y: None
    spacing: app.padding, app.padding
    cols: 1 if app.simple_interface else 2
    height: self.minimum_height
    BoxLayout:
        height: app.button_scale
        size_hint_y: None
        orientation: 'horizontal'
        ShortLabel:
            text: 'Server And Folder: '
        NormalInput:
            multiline: False
            text: root.owner.ftp_address
            input_filter: root.owner.ftp_filter
            on_focus: root.owner.set_ftp_address(self)
    BoxLayout:
        height: app.button_scale
        size_hint_y: None
        orientation: 'horizontal'
        NormalToggle:
            size_hint_x: 1
            text: 'Passive Mode' if root.owner.ftp_passive else 'Active Mode'
            state: 'down' if root.owner.ftp_passive else 'normal'
            on_press: root.owner.set_ftp_passive(self)
        BoxLayout:
            orientation: 'horizontal'
            size_hint_x: 1
            ShortLabel:
                text: 'Port: '
            NormalInput:
                multiline: False
                text: str(root.owner.ftp_port)
                input_filter: 'int'
                on_focus: root.owner.set_ftp_port(self)
    BoxLayout:
        height: app.button_scale
        size_hint_y: None
        orientation: 'horizontal'
        ShortLabel:
            text: 'Login: '
        NormalInput:
            multiline: False
            text: root.owner.ftp_user
            on_focus: root.owner.set_ftp_user(self)
    BoxLayout:
        height: app.button_scale
        size_hint_y: None
        orientation: 'horizontal'
        ShortLabel:
            text: 'Password: '
        NormalInput:
            password: True
            multiline: False
            text: root.owner.ftp_password
            on_focus: root.owner.set_ftp_password(self)
""")

class FTPToggleSettings(GridLayout):
    """Widget layout for the export to ftp settings on the export dialog."""
    owner = ObjectProperty()