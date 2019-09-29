from kivy.app import App
from kivy.uix.settings import SettingItem

from kivy.lang.builder import Builder

Builder.load_string("""
<SettingsBackToLibraryButton>:
    WideButton:
        text: 'Back to Library'
        size: root.size
        pos: root.pos
        font_size: '15sp'
        on_release: root.show_database()

""")
class SettingsBackToLibraryButton(SettingItem):
    """Widget that opens the theme screen"""
    def show_database(self):
        app = App.get_running_app()
        app.close_settings()
        app.show_database()