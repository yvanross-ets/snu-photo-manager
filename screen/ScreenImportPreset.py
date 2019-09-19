import os
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty

from screenImporting.ImportPreset import ImportPreset

try:
    from shutil import disk_usage
except:
    disk_usage = None

from generalcommands import local_path
from generalElements.NormalLabel import NormalLabel

from kivy.lang.builder import Builder
Builder.load_string("""
<ScreenImportPreset>:
    canvas.before:
        Color:
            rgba: app.theme.background
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        MainHeader:
            NormalButton:
                text: 'Back To Library'
                on_release: app.show_database()
            HeaderLabel:
                text: 'Import Photos'
            InfoLabel:
            DatabaseLabel:
            SettingsButton:
        BoxLayout:
            orientation: 'horizontal'
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: .75
                Header:
                    size_hint_y: None
                    height: app.button_scale
                    NormalLabel:
                        text: 'Select An Import Preset:'
                    NormalButton:
                        id: newPresetButton
                        disabled: True
                        text: 'New Preset'
                        on_release: root.add_preset()
                MainArea:
                    Scroller:
                        id: presetsContainer
                        do_scroll_x: False
                        GridLayout:
                            height: self.minimum_height
                            size_hint_y: None
                            cols: 1
                            id: presets

            LargeBufferX:
            StackLayout:
                size_hint_x: .25
                Scroller:
                    size_hint_y: 1
                    GridLayout:
                        size_hint_y: None
                        height: self.minimum_height
                        cols: 1
                        NormalLabel:
                            text_size: self.width, None
                            height: self.texture_size[1]
                            text: 'Naming Method Details\\n\\nYou may type in an import folder template into this field, the folder names will be generated from the template.  The following characters are not allowed: . \\ / : * ? < > | \\nEncase the title and surrounding characters in < > to hide the surrounding characters if the title is not set.  "Folder< - %t>" would result in "Folder" if Title is not set.\\n\\nThe following keys will be replaced in the input to create a folder name:'
                        GridLayout:
                            cols: 3
                            size_hint_y: None
                            size_hint_y: 1
                            height: (app.button_scale * 11)
                            ShortLabel:
                                text: '%Y'
                            ShortLabel:
                                text: ' - '
                            LeftNormalLabel:
                                text: 'Full Year (2016)'

                            ShortLabel:
                                text: '%y'
                            ShortLabel:
                                text: ' - '
                            LeftNormalLabel:
                                text: 'Year Decade Digits (16)'

                            ShortLabel:
                                text: '%B'
                            ShortLabel:
                                text: ' - '
                            LeftNormalLabel:
                                text: 'Full Month Name (January)'

                            ShortLabel:
                                text: '%b'
                            ShortLabel:
                                text: ' - '
                            LeftNormalLabel:
                                text: 'Month In 3 Letters (Jan)'

                            ShortLabel:
                                text: '%M'
                            ShortLabel:
                                text: ' - '
                            LeftNormalLabel:
                                text: 'Month In 2 Digits (01)'

                            ShortLabel:
                                text: '%m'
                            ShortLabel:
                                text: ' - '
                            LeftNormalLabel:
                                text: 'Month In Digits, No Padding (1)'

                            ShortLabel:
                                text: '%D'
                            ShortLabel:
                                text: ' - '
                            LeftNormalLabel:
                                text: 'Day Of Month In 2 Digits (04)'

                            ShortLabel:
                                text: '%d'
                            ShortLabel:
                                text: ' - '
                            LeftNormalLabel:
                                text: 'Day Of Month, No Padding (4)'

                            ShortLabel:
                                text: '%T'
                            ShortLabel:
                                text: ' - '
                            LeftNormalLabel:
                                text: 'Folder Title (My Pictures)'

                            ShortLabel:
                                text: '%t'
                            ShortLabel:
                                text: ' - '
                            LeftNormalLabel:
                                text: 'Folder Title With Underscores (My_Pictures)'

                            ShortLabel:
                                text: '%%'
                            ShortLabel:
                                text: ' - '
                            LeftNormalLabel:
                                text: 'Percent Sign (%)'



""")


class ScreenImportPreset(Screen):
    """Screen layout for beginning the import photos process.
    Displays import presets and allows the user to pick one.
    """

    popup = None
    selected_import = NumericProperty(-1)

    def dismiss_extra(self):
        """Dummy function, not valid for this screen, but the app calls it when escape is pressed."""
        return False

    def import_preset(self):
        """Activates the import process using the selected import preset."""

        app = App.get_running_app()
        preset = app.imports[self.selected_import]
        if not preset['import_from']:
            app.message("Please Set An Import Directory.")
            return
        good_paths = []
        for path in preset['import_from']:
            if os.path.exists(path):
                good_paths.append(path)
        if not good_paths:
            app.message("Directories to import photo from do not exist.")
            return
        if not os.path.exists(preset['import_to']):
            app.message("Directory to import photo to do not exist or is not accessible.")
            return
        database_folders = app.config.get('Database Directories', 'paths')
        database_folders = local_path(database_folders)
        if database_folders.strip(' '):
            databases = database_folders.split(';')
        else:
            databases = []
        if preset['import_to'] not in databases:
            app.message("Please Set A Database To Import To.")
            return
        app.importing_screen.import_to = preset['import_to']
        app.importing_screen.naming_method = preset['naming_method']
        app.importing_screen.delete_originals = preset['delete_originals']
        app.importing_screen.import_from = preset['import_from']
        app.importing_screen.single_folder = preset['single_folder']
        app.show_importing()

    def add_preset(self):
        """Creates a new blank import preset."""

        app = App.get_running_app()
        app.import_preset_new()
        self.selected_import = len(app.imports) - 1
        self.update_treeview()

    def on_leave(self):
        """Called when the screen is left.  Save the import presets."""

        app = App.get_running_app()
        app.import_preset_write()
        presets = self.ids['presets']
        presets.clear_widgets()

    def on_enter(self):
        """Called on entering the screen, updates the treeview and variables."""

        self.selected_import = -1
        self.update_treeview()

    def update_treeview(self):
        """Clears and redraws all the import presets in the treeview."""

        app = App.get_running_app()
        presets = self.ids['presets']

        #Clear old presets
        presets.clear_widgets()

        #Check if screenDatabase folders are set, cant import without somewhere to import to.
        database_folders = app.config.get('Database Directories', 'paths')
        database_folders = local_path(database_folders)
        if database_folders.strip(' '):
            databases = database_folders.split(';')
        else:
            databases = []
        new_preset_button = self.ids['newPresetButton']
        if databases:
            new_preset_button.disabled = False
            for index, import_preset in enumerate(app.imports):
                preset = ImportPreset(index=index, text=import_preset['title'], owner=self, import_to=import_preset['import_to'])
                preset.data = import_preset
                if index == self.selected_import:
                    preset.expanded = True
                presets.add_widget(preset)
        else:
            new_preset_button.disabled = True
            presets.add_widget(NormalLabel(text="You Must Set Up A Database Before Importing Photos"))

    def has_popup(self):
        """Detects if the current screen has a popup active.
        Returns: True or False
        """

        if self.popup:
            if self.popup.open:
                return True
        return False

    def dismiss_popup(self, *_):
        """Close a currently open popup for this screen."""

        if self.popup:
            self.popup.dismiss()
            self.popup = None

    def key(self, key):
        """Dummy function, not valid for this screen but the app calls it."""

        if not self.popup or (not self.popup.open):
            pass


