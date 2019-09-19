from kivy.app import App
from kivy.uix.settings import SettingItem
from kivy.lang.builder import Builder

Builder.load_string("""
<SettingDatabaseClean>:
    WideButton:
        text: 'Deep Clean Database'
        size: root.size
        pos: root.pos
        font_size: '15sp'
        disabled: app.database_scanning
        on_release: root.database_clean()

""")

class SettingDatabaseClean(SettingItem):
    """Database deep-clean widget for the settings screen."""
    def database_clean(self):
        app = App.get_running_app()
        app.database_clean(deep=True)