from kivy.app import App
from kivy.uix.settings import SettingItem

from kivy.lang.builder import Builder

Builder.load_string("""
<SettingsThemeButton>:
    WideButton:
        text: 'Theme Settings'
        size: root.size
        pos: root.pos
        font_size: '15sp'
        on_release: root.show_theme()

""")
class SettingsThemeButton(SettingItem):
    """Widget that opens the theme screen"""
    def show_theme(self):
        app = App.get_running_app()
        app.close_settings()
        app.show_theme()