from kivy.app import App
from kivy.uix.settings import SettingItem
from kivy.lang.builder import Builder

Builder.load_string("""
<SettingDatabaseBackup>:
    WideButton:
        text: 'Backup Photo Database'
        size: root.size
        pos: root.pos
        font_size: '15sp'
        disabled: app.database_scanning
        on_release: root.database_backup()
""")

class SettingDatabaseBackup(SettingItem):
    """Database backup restore widget for the settings screen."""
    def database_backup(self):
        app = App.get_running_app()
        app.database_backup()