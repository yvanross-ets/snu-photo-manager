from kivy.uix.settings import SettingsWithNoMenu

from screenSettings.SettingString import SettingString
from screenSettings.SettingNumeric import SettingNumeric
from screenSettings.SettingsThemeButton import SettingsThemeButton
from screenSettings.SettingMultiDirectory import SettingMultiDirectory
from screenSettings.SettingDatabaseImport import SettingDatabaseImport
from screenSettings.SettingDatabaseRestore import SettingDatabaseRestore
from screenSettings.SettingDatabaseClean import SettingDatabaseClean
from screenSettings.SettingDatabaseBackup import SettingDatabaseBackup
from screenSettings.SettingsAboutButton import SettingAboutButton


class PhotoManagerSettings(SettingsWithNoMenu):
    """Expanded settings class to add new settings buttons and types."""

    def __init__(self, **kwargs):
        super(PhotoManagerSettings, self).__init__(**kwargs)
        self.register_type('string', SettingString)
        self.register_type('numeric', SettingNumeric)
        self.register_type('multidirectory', SettingMultiDirectory)
        self.register_type('themescreen', SettingsThemeButton)
        self.register_type('databaseimport', SettingDatabaseImport)
        self.register_type('databaseclean', SettingDatabaseClean)
        self.register_type('aboutbutton', SettingAboutButton)
        self.register_type('databaserestore', SettingDatabaseRestore)
        self.register_type('databasebackup', SettingDatabaseBackup)