from kivy.app import App
from kivy.uix.settings import SettingItem

from kivy.lang.builder import Builder

Builder.load_string("""
<SettingDatabaseImport>:
    WideButton:
        text: 'Import/Rescan Database'
        size: root.size
        pos: root.pos
        font_size: '15sp'
        disabled: app.database_scanning
        on_release: root.database_import()
""")
class SettingDatabaseImport(SettingItem):
    """Database scan/import widget for the settings screen."""
    def database_import(self):
        app = App.get_running_app()
        app.database_import()