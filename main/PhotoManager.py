import json
import os
import sqlite3
import threading
import time
from kivy.modules import inspector
from kivy.core.window import Window
from kivy.modules import inspector
try:
    from configparser import ConfigParser
except:
    from six.moves import configparser
from sqlalchemy import create_engine
from models.create_database import create_database
from sqlalchemy.orm import sessionmaker
from models.PhotosTags import Folder

from shutil import copyfile, move, rmtree
from subprocess import call

from PIL import Image, ImageEnhance

from kivy import platform
from kivy.app import App
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import BooleanProperty, NumericProperty, StringProperty, ObjectProperty, ListProperty
from kivy.uix.screenmanager import SlideTransition, NoTransition, ScreenManager

from generalcommands import  agnostic_photoinfo, local_photoinfo, to_bool, local_path, naming, \
  agnostic_path, local_paths, list_folders, isfile2, local_thumbnail, get_folder_info
from generalconstants import imagetypes, movietypes, desktop, naming_method_default, kivy_version_primary, \
  kivy_version_secondary, interface_multiplier
from generalElements.popups.InputMenu import InputMenu
from generalElements.treeviews.TreenodeDrag import TreenodeDrag
from generalElements.photos.PhotoDrag import PhotoDrag
from generalElements.popups.MessagePopup import MessagePopup
from generalElements.popups.NormalPopup import NormalPopup
from main import Theme
from main.MainWindow import MainWindow
from main.SQLMultiThreadOK import SQLMultiThreadOK
from screens.screenDatabase import ScreenDatabase
from screens.screenDatabaseRestore import ScreenDatabaseRestore
from screens.screenDatabaseTransfer import ScreenDatabaseTransfer
from screenSettings.AboutPopup import AboutPopup
from screenSettings.PhotoManagerSettings import PhotoManagerSettings
from send2trash import send2trash
from main.Theme import Theme


class PhotoManager(App):
    """Main class of the app."""

    timer_value = 0
    button_update = BooleanProperty(False)
    settings_open = BooleanProperty(False)
    right_panel = BooleanProperty(False)
    last_width = NumericProperty(0)
    button_scale = NumericProperty(40)
    text_scale = NumericProperty(12)
    data_directory = StringProperty('')
    app_location = StringProperty('')
    database_auto_rescanner = ObjectProperty()
    database_auto_rescan_timer = NumericProperty(0)
    database_update_text = StringProperty('')
    showhelp = BooleanProperty(True)
    infotext = StringProperty('')
    infotext_setter = ObjectProperty()
    single_database = BooleanProperty(True)
    simple_interface = BooleanProperty(False)

    #Theming variables
    icon = 'data/icon.png'
    theme = ObjectProperty()
    selected_color = (0.5098, 0.8745, 0.6588, .5)
    list_background_odd = (0, 0, 0, 0)
    list_background_even = (0, 0, 0, .1)
    padding = NumericProperty(10)
    popup_x = 640
    animations = True
    animation_length = .2

    interpolation = StringProperty('Catmull-Rom')  #Interpolation mode of the curves dialog.
    fullpath = StringProperty()
    database_scanning = BooleanProperty(False)
    database_sort = StringProperty('')
    # album_sort = StringProperty('')
    database_sort_reverse = BooleanProperty(False)
    # album_sort_reverse = BooleanProperty(False)
    thumbsize = 256  #Size in pixels of the long side of any generated thumbnails
    settings_cls = PhotoManagerSettings
    target = StringProperty()
    type = StringProperty('None')
    photo = StringProperty('')
    imports = []
    exports = []
    # albums = []
    programs = []
    database_path = None
    shift_pressed = BooleanProperty(False)
    cancel_scanning = BooleanProperty(False)
    export_target = StringProperty()
    export_type = StringProperty()
    encoding_presets = ListProperty()
    selected_encoder_preset = StringProperty()

    #Widget holders
    drag_image = ObjectProperty()
    drag_treenode = ObjectProperty()
    main_layout = ObjectProperty()  #Main layout root widget
    screen_manager = ObjectProperty()
    database_screen = ObjectProperty()
    album_screen = ObjectProperty()
    importing_screen = ObjectProperty()
    database_restore_screen = ObjectProperty()
    scanningthread = None
    scanningpopup = None
    popup = None
    bubble = None
    session = None

    about_text = StringProperty()

    def timer(self, *_):
        start_time = time.perf_counter()
        timed = start_time - self.timer_value
        self.timer_value = start_time
        return timed

    def popup_bubble(self, text_input, pos):
        self.close_bubble()
        text_input.unfocus_on_touch = False
        self.bubble = InputMenu(owner=text_input)
        window = self.root_window
        window.add_widget(self.bubble)
        posx = pos[0]
        posy = pos[1]
        #check position to ensure its not off screen
        if posx + self.bubble.width > window.width:
            posx = window.width - self.bubble.width
        if posy + self.bubble.height > window.height:
            posy = window.height - self.bubble.height
        self.bubble.pos = [posx, posy]

    def close_bubble(self, *_):
        if self.bubble:
            self.bubble.owner.unfocus_on_touch = True
            window = self.root_window
            window.remove_widget(self.bubble)
            self.bubble = None

    def save_current_theme(self):
        self.theme.save()

    def set_single_database(self):
        databases = self.get_database_directories()
        if len(databases) > 1:
            self.single_database = False
        else:
            self.single_database = True

    def message(self, text, timeout=20):
        """Sets the app.infotext variable to a specific message, and clears it after a set amount of time."""

        self.infotext = text
        if self.infotext_setter:
            self.infotext_setter.cancel()
        self.infotext_setter = Clock.schedule_once(self.clear_message, timeout)

    def clear_message(self, *_):
        self.infotext = ''

    def clear_database_update_text(self, *_):
        self.database_update_text = ''

    def refresh_photo(self, fullpath, force=False, no_photoinfo=False, data=False, skip_isfile=False):
        """Checks if a file's modified date has changed, updates photoinfo and thumbnail if it has"""

        if data:
            old_photoinfo = data
        else:
            old_photoinfo = self.Photo.exist(fullpath)
        if old_photoinfo:
            #Photo is in screenDatabase, check if it has been modified in any way
            photo_filename = os.path.join(old_photoinfo[2], old_photoinfo[0])
            if skip_isfile or os.path.isfile(photo_filename):
                #file still exists
                modified_date = int(os.path.getmtime(photo_filename))
                if modified_date != old_photoinfo[7] or force:
                    #file has been modified somehow, need to update data
                    new_photoinfo = FileInfo([old_photoinfo[0], old_photoinfo[2]], import_mode=True, modified_date=modified_date)
                    photoinfo = list(old_photoinfo)
                    photoinfo[7] = new_photoinfo.tags
                    photoinfo[13] = new_photoinfo.edited
                    self.Photo.update(photoinfo)
                    if not no_photoinfo:
                        self.update_photoinfo(folders=[photoinfo[1]])
                    self.Photo.thumbnail_update(photoinfo[0], photoinfo[2], photoinfo[7], photoinfo[13], force=True)
                    if self.screen_manager.current == 'album':
                        album_screen = self.screen_manager.get_screen('album')
                        album_screen.clear_cache()
                    return photoinfo
        return False

    def toggle_quicktransfer(self, button):
        if self.config.get("Settings", "quicktransfer") == '0':
            self.config.set("Settings", "quicktransfer", '1')
            button.state = 'normal'
        else:
            self.config.set("Settings", "quicktransfer", '0')
            button.state = 'down'

    def about(self):
        """Creates and opens a dialog telling about this program."""

        title = "About Snu Photo Manager"
        self.popup = AboutPopup(title=title)
        self.popup.open()

    def canprint(self):
        """Check if in desktop mode.
        Returns: Boolean True if in desktop mode, False if not.
        """

        if desktop:
            return True
        else:
            return False

    def print_photo(self):
        """Calls the operating system to print the currently viewed photo."""

        photo_info = self.Photo.exist(self.fullpath)
        if photo_info:
            photo_file = os.path.abspath(os.path.join(photo_info[2], photo_info[0]))
            self.message("Printing photo...")
            os.startfile(photo_file, "print")

    def program_run(self, index, button):
        """Loads the currently viewed photo in an external program using an external program preset.
        Argument:
            index: Integer, index of the preset to use.
            button: Widget, the button that called this function.
        """

        name, command, argument = self.programs[index]
        if os.path.isfile(command):
            button.disabled = True  # Disable the button so the user knows something is happening
            photo_info = self.Photo.exist(self.fullpath)
            if photo_info:
                photo_file = os.path.join(photo_info[2], photo_info[0])
                abs_photo = os.path.abspath(photo_file)
                argument_replace = argument.replace('%i', '"'+abs_photo+'"')
                argument_replace = argument_replace.replace('%%', '%')

                run_command = command+' '+argument_replace
                Clock.schedule_once(lambda *dt: self.program_run_finish(run_command, photo_info, button))
        else:
            self.popup_message(text='Not A Valid Program')

    def program_run_finish(self, command, photo_info, button):
        """Finishes the program_run command, must be delayed by a frame to allow the button to be visibly disabled."""

        call(command)
        self.refresh_photo(photo_info[0])
        button.disabled = False

    def program_save(self, index, name, command, argument):
        """Updates an external program preset.
        Arguments:
            index: Integer, index of the preset to run.
            name: Program name
            command: Path to the program executable.
            argument: Extra command arguments
        """

        self.programs[index] = [name, command, argument]
        self.program_export()

    def program_add(self, name, command, argument):
        """Creates a new external program preset.
        Arguments:
            name: Program name
            command: Path to the program executable.
            argument: Extra command arguments
        """

        self.programs.append([name, command, argument])
        self.program_export()

    def program_remove(self, index):
        """Deletes an external program preset.
        Argument:
            index: Integer, preset index to delete.
        """

        del self.programs[index]
        self.program_export()

    def program_export(self):
        """Save current external program presets to the config file."""

        configfile = ConfigParser(interpolation=None)
        for index, preset in enumerate(self.programs):
            name, command, argument = preset
            section = str(index)
            configfile.add_section(section)
            configfile.set(section, 'name', name)
            configfile.set(section, 'command', command)
            configfile.set(section, 'argument', argument)
        with open(self.data_directory+os.path.sep+'programs.ini', 'w') as config:
            configfile.write(config)

    def program_import(self):
        """Import external program presets from the config file."""

        self.programs = []
        filename = self.data_directory+os.path.sep+'programs.ini'
        if os.path.isfile(filename):
            configfile = ConfigParser(interpolation=None)
            configfile.read(filename)
            program_presets = configfile.sections()
            for preset in program_presets:
                program_preset = dict(configfile.items(preset))
                name = program_preset['name']
                command = program_preset['command']
                argument = program_preset['argument']
                self.programs.append([name, command, argument])

    def save_photoinfo(self, target, save_location, container_type='folder', photos=list(), newnames=False):
        """Save relavent photoinfo files for a folder, album, tag, Persons or specified photos.
        Arguments:
            target: String, screenDatabase identifier for the path where the photos are.
            save_location: String, full absolute path to the folder where the photoinfo file should be saved.
            container_type: String, defaults to 'folder', may be folder, album or tag.
            photos: Optional, List of photoinfo objects to save the photoinfo for.
            newnames:
        """

        description = ''
        title = ''

        #If photos are not provided, find them for the given target.
        if not photos:
            if container_type == 'tag':
                photos = self.Tag.photos(target)
                title = "Photos tagged as '"+target+"'"
            elif container_type == 'person':
                photos = self.Person.photos(target)
                title = "Photos include person as '" + target + "'"
            elif container_type == 'folder':
                folder_info = self.Folder.exist(target)
                if folder_info:
                    title = folder_info[1]
                    description = folder_info[2]
                photos = self.Photo.by_folder(target)
            else:
                return

        if photos:
            if newnames:
                if len(newnames) != len(photos):
                    newnames = False
            #Set up config file
            configfile = ConfigParser(interpolation=None)
            config_filename = os.path.join(save_location, '.photoinfo.ini')
            if os.path.exists(config_filename):
                os.remove(config_filename)
            configfile.add_section('Album')
            configfile.set('Album', 'title', title)
            configfile.set('Album', 'description', description)

            #Save photo info
            for index, photo in enumerate(photos):
                if newnames:
                    photo_filename = newnames[index]
                else:
                    photo_filename = os.path.basename(photo[0])
                configfile.add_section(photo_filename)
                configfile.set(photo_filename, 'tags', photo[8])
                configfile.set(photo_filename, 'persons', photo[14])
                configfile.set(photo_filename, 'owner', photo[11])
                configfile.set(photo_filename, 'edited', str(photo[9]))
                configfile.set(photo_filename, 'import_date', str(photo[6]))
                configfile.set(photo_filename, 'rename', photo[5])
                configfile.set(photo_filename, 'export', str(photo[12]))
            try:
                with open(config_filename, 'w') as config:
                    configfile.write(config)
            except:
                pass

    def update_photoinfo(self, folders=list()):
        """Updates the photoinfo files in given folders.
        Arguments:
            folders: List containing Strings for screenDatabase-relative paths to each folder.
        """

        if self.config.get("Settings", "photoinfo"):
            databases = self.get_database_directories()
            folders = list(set(folders))
            for folder in folders:
                for database in databases:
                    full_path = os.path.join(database, folder)
                    if os.path.isdir(full_path):
                        self.save_photoinfo(target=folder, save_location=full_path)



    def on_config_change(self, config, section, key, value):
        self.animations = to_bool(self.config.get("Settings", "animations"))
        self.set_transition()
        self.simple_interface = to_bool(self.config.get("Settings", "simpleinterface"))
        self.thumbsize = int(self.config.get("Settings", "thumbsize"))
        if key == 'buttonsize' or key == 'textsize':
            self.rescale_interface(force=True)
            Clock.schedule_once(self.database_screen.on_enter)

    def build_config(self, config):
        """Setup config file if it is not found."""

        if desktop:
            simple_interface = 0
        else:
            simple_interface = 1
        config.setdefaults(
            'Settings', {
                'photoinfo': 1,
                'buttonsize': 100,
                'textsize': 100,
                'thumbsize': 256,
                'leftpanel': 0.2,
                'rightpanel': 0.2,
                'videoautoplay': 0,
                'precache': 1,
                'rememberview': 1,
                'viewtype': '',
                'viewtarget': '',
                'viewdisplayable': 0,
                'autoscan': 0,
                'quicktransfer': 0,
                'lowmem': 0,
                'simpleinterface': simple_interface,
                'backupdatabase': 1,
                'rescanstartup': 0,
                'animations': 1,
                'databasescale': 100
            })
        config.setdefaults(
            'Database Directories', {
                'paths': '',
                'achive': 0
            })
        config.setdefaults(
            'Sorting', {
                'database_sort': 'Name',
                'database_sort_reverse': 0,
            })
        config.setdefaults(
            'Presets', {
                'import': 0,
                'export': 0,
                'encoding': ''
            })

    def build_settings(self, settings):
        """Kivy settings dialog panel.
        Settings types: title, bool, numeric, options, string, path
        """

        settingspanel = []
        settingspanel.append({
            "type": "aboutbutton",
            "title": "",
            "section": "Settings",
            "key": "photoinfo"
        })
        settingspanel.append({
            "type": "backToLibrary",
            "title": "Back to library",
            "section": "Settings",
            "key": "photoinfo"
        })

        settingspanel.append({
            "type": "themescreen",
            "title": "",
            "section": "Settings",
            "key": "photoinfo"
        })
        settingspanel.append({
            "type": "multidirectory",
            "title": "Database Directories",
            "desc": "Folders For Image Database",
            "section": "Database Directories",
            "key": "paths"
        })
        settingspanel.append({
            "type": "databaseimport",
            "title": "",
            "section": "Database Directories",
            "key": "paths"
        })
        settingspanel.append({
            "type": "databaseclean",
            "title": "",
            "desc": "Remove all missing files in screenDatabase.  Warning: Make sure all remote directories are accessible",
            "section": "Database Directories",
            "key": "paths"
        })
        settingspanel.append({
            "type": "databasebackup",
            "title": "",
            "desc": "Creates a backup of the current photo databases",
            "section": "Database Directories",
            "key": "paths"
        })
        settingspanel.append({
            "type": "databaserestore",
            "title": "",
            "desc": "Restore and reload screenDatabase backups from previous run if they exist",
            "section": "Database Directories",
            "key": "paths"
        })
        settingspanel.append({
            "type": "numeric",
            "title": "Button Size Percent",
            "desc": "Scale Percentage Of Interface Buttons",
            "section": "Settings",
            "key": "buttonsize"
        })
        settingspanel.append({
            "type": "numeric",
            "title": "Text Size Percent",
            "desc": "Scale percentage of interface text",
            "section": "Settings",
            "key": "textsize"
        })
        settingspanel.append({
            "type": "numeric",
            "title": "Thumbnail Size",
            "desc": "Size in pixels of generated thumbnails",
            "section": "Settings",
            "key": "thumbsize"
        })
        settingspanel.append({
            "type": "numeric",
            "title": "Database Thumbs Scale",
            "desc": "Default pecentage scale for thumbnails in the screenDatabase screen",
            "section": "Settings",
            "key": "databasescale"
        })
        settingspanel.append({
            "type": "bool",
            "title": "Save .photoinfo.ini Files",
            "desc": "Auto-save .photoinfo.ini files in folders when photos are changed",
            "section": "Settings",
            "key": "photoinfo"
        })
        settingspanel.append({
            "type": "bool",
            "title": "Auto-Play Videos On View",
            "desc": "Automatically play videos when they are viewed in album mode",
            "section": "Settings",
            "key": "videoautoplay"
        })
        settingspanel.append({
            "type": "bool",
            "title": "Auto-Cache Images When Browsing",
            "desc": "Automatically cache the next and previous images when browsing photos",
            "section": "Settings",
            "key": "precache"
        })
        settingspanel.append({
            "type": "bool",
            "title": "Remember Last Album View",
            "desc": "Remembers and returns to the last folder that was being viewed on last run",
            "section": "Settings",
            "key": "rememberview"
        })
        settingspanel.append({
            "type": "bool",
            "title": "Simplify Interface For Smaller Screens",
            "desc": "Removes some components of the interface.  Intended for phones or touch screen devices.",
            "section": "Settings",
            "key": "simpleinterface"
        })
        settingspanel.append({
            "type": "bool",
            "title": "Animate Interface",
            "desc": "Animate various elements of the interface.  Disable this on slow computers.",
            "section": "Settings",
            "key": "animations"
        })
        settingspanel.append({
            "type": "bool",
            "title": "Low Memory Mode",
            "desc": "For older computers that show larger images as black, display all images at a smaller size",
            "section": "Settings",
            "key": "lowmem"
        })
        settingspanel.append({
            "type": "numeric",
            "title": "Auto-Rescan Database Interval In Minutes",
            "desc": "Auto-rescan screenDatabase every number of minutes.  0 will never auto-scan.  Setting this too low will slow the system down.",
            "section": "Settings",
            "key": "autoscan"
        })
        settingspanel.append({
            "type": "bool",
            "title": "Rescan Photo Database On Startup",
            "desc": "Automatically scan and update the photo screenDatabase on each restart.  Prevents editing functions from being done until finished.",
            "section": "Settings",
            "key": "rescanstartup"
        })
        settingspanel.append({
            "type": "bool",
            "title": "Backup Photo Database On Startup",
            "desc": "Automatically make a copy of the photo screenDatabase on each restart.  Will increase startup time when large databases are loaded.",
            "section": "Settings",
            "key": "backupdatabase"
        })
        settings.add_json_panel('App', self.config, data=json.dumps(settingspanel))

    def has_database(self, *_):
        databases = self.get_database_directories()
        if databases:
            return True
        else:
            return False

    def database_auto_rescan(self, *_):
        rescan_time = float(self.config.get("Settings", "autoscan"))
        if rescan_time > 0:
            self.database_auto_rescan_timer = self.database_auto_rescan_timer - 1
            if self.database_auto_rescan_timer < 1:
                self.database_rescan()
                self.database_auto_rescan_timer = rescan_time

    def on_start(self):
        """Function called when the app is first started.
        Add a custom keyboard hook so key buttons can be intercepted.
        """

        EventLoop.window.bind(on_keyboard=self.hook_keyboard)
        if not self.has_database():
            self.open_settings()
        self.database_auto_rescan_timer = float(self.config.get("Settings", "autoscan"))
        self.database_auto_rescanner = Clock.schedule_interval(self.database_auto_rescan, 60)
        self.rescale_interface(force=True)
        Window.bind(on_draw=self.rescale_interface)

    def on_pause(self):
        """Function called when the app is paused or suspended on a mobile platform.
        Saves all settings and data.
        """

        if self.main_layout:
            self.config.write()
            self.__commit_database()
        return True

    def on_resume(self):
        print('Resuming App...')

    def on_stop(self):
        """Function called just before the app is closed.
        Saves all settings and data.
        """
        if self.database_scanning:
            self.cancel_database_import()
            self.scanningthread.join()
        self.config.write()

    def open_settings(self, *largs):
        self.clear_drags()
        self.settings_open = True
        super().open_settings(*largs)

    def close_settings(self, *largs):
        self.settings_open = False
        super().close_settings(*largs)

    def hook_keyboard(self, window, scancode, *_):
        """This function receives keyboard events"""

        self.close_bubble()

        if self.settings_open:
            if scancode == 27:
                if self.popup:
                    self.popup.dismiss()
                    self.popup = None
                    return True
                else:
                    self.close_settings()
                    return True
        else:
            del window
            current_screen = self.screen_manager.current_screen
            if scancode == 97:
                #a key
                current_screen.key('a')
            if scancode == 276:
                #left key
                current_screen.key('left')
            if scancode == 275:
                #right key
                current_screen.key('right')
            if scancode == 273:
                #up key
                current_screen.key('up')
            if scancode == 274:
                #down key
                current_screen.key('down')
            if scancode == 32:
                #space key
                current_screen.key('space')
            if scancode == 13:
                #enter key
                current_screen.key('enter')
            if scancode == 127 or scancode == 8:
                #delete and backspace key
                current_screen.key('delete')
            if scancode == 9:
                #tab key
                current_screen.key('tab')
            if scancode == 282:
                #f1 key
                current_screen.key('f1')
            if scancode == 283:
                #f2 key
                current_screen.key('f2')
            if scancode == 284:
                #f3 key
                current_screen.key('f3')
            if scancode == 285:
                #f4 key
                current_screen.key('f4')
            if scancode == 27:  #Escape
                self.clear_drags()
                if Window.keyboard_height > 0:
                    Window.release_all_keyboards()
                    return True
                elif not self.screen_manager.current_screen:
                    return False
                #elif self.database_scanning:
                #    self.cancel_database_import()
                #    return True
                elif self.screen_manager.current_screen.dismiss_extra():
                    return True
                elif self.screen_manager.current_screen.has_popup():
                    self.screen_manager.current_screen.dismiss_popup()
                    return True
                elif self.screen_manager.current != 'screenDatabase':
                    if self.screen_manager.current == 'photo':
                        self.show_album()
                    else:
                        self.show_database()
                    return True

    def setup_import_presets(self):
        """Reads the import presets from the config file and saves them to the app.imports variable."""

        self.imports = []
        filename = self.data_directory+os.path.sep+'imports.ini'
        if os.path.isfile(filename):
            try:
                configfile = ConfigParser(interpolation=None)
                configfile.read(filename)
                import_presets = configfile.sections()
                for preset in import_presets:
                    try:
                        import_preset = dict(configfile.items(preset))
                        import_title = import_preset['title']
                        import_to = local_path(import_preset['import_to'])
                        naming_method = import_preset['naming_method']
                        if not naming(naming_method, title=''):
                            naming_method = naming_method_default
                        delete_originals = to_bool(import_preset['delete_originals'])
                        single_folder = to_bool(import_preset['single_folder'])
                        if import_preset['import_from']:
                            import_from_folders = local_path(import_preset['import_from'])
                            import_from = import_from_folders.split('|')
                        else:
                            import_from = []
                        self.imports.append({
                            'title': import_title,
                            'import_to': import_to,
                            'naming_method': naming_method,
                            'delete_originals': delete_originals,
                            'single_folder': single_folder,
                            'import_from': import_from})
                    except:
                        pass
            except:
                pass

    def setup_export_presets(self):
        """Reads the export presets from the config file and saves them to the app.exports variable."""

        self.exports = []
        filename = self.data_directory+os.path.sep+'exports.ini'
        if os.path.isfile(filename):
            try:
                configfile = ConfigParser(interpolation=None)
                configfile.read(filename)
                export_presets = configfile.sections()
                for preset in export_presets:
                    try:
                        export_preset = dict(configfile.items(preset))
                        name = export_preset['name']
                        export = export_preset['export']
                        ftp_address = export_preset['ftp_address']
                        ftp_user = export_preset['ftp_user']
                        ftp_password = export_preset['ftp_password']
                        ftp_passive = to_bool(export_preset['ftp_passive'])
                        ftp_port = int(export_preset['ftp_port'])
                        export_folder = local_path(export_preset['export_folder'])
                        create_subfolder = to_bool(export_preset['create_subfolder'])
                        export_info = to_bool(export_preset['export_info'])
                        scale_image = to_bool(export_preset['scale_image'])
                        scale_size = int(export_preset['scale_size'])
                        scale_size_to = export_preset['scale_size_to']
                        jpeg_quality = int(export_preset['jpeg_quality'])
                        watermark = to_bool(export_preset['watermark'])
                        watermark_image = local_path(export_preset['watermark_image'])
                        watermark_opacity = int(export_preset['watermark_opacity'])
                        watermark_horizontal = int(export_preset['watermark_horizontal'])
                        watermark_vertical = int(export_preset['watermark_vertical'])
                        watermark_size = int(export_preset['watermark_size'])
                        if export_preset['ignore_tags']:
                            ignore_tags = export_preset['ignore_tags'].split('|')
                        else:
                            ignore_tags = []
                        export_videos = to_bool(export_preset['export_videos'])
                        self.exports.append({
                            'name': name,
                            'export': export,
                            'ftp_address': ftp_address,
                            'ftp_user': ftp_user,
                            'ftp_password': ftp_password,
                            'ftp_passive': ftp_passive,
                            'ftp_port': ftp_port,
                            'export_folder': export_folder,
                            'create_subfolder': create_subfolder,
                            'export_info': export_info,
                            'scale_image': scale_image,
                            'scale_size': scale_size,
                            'scale_size_to': scale_size_to,
                            'jpeg_quality': jpeg_quality,
                            'watermark': watermark,
                            'watermark_image': watermark_image,
                            'watermark_opacity': watermark_opacity,
                            'watermark_horizontal': watermark_horizontal,
                            'watermark_vertical': watermark_vertical,
                            'watermark_size': watermark_size,
                            'ignore_tags': ignore_tags,
                            'export_videos': export_videos})
                    except:
                        pass
            except:
                pass

    def export_preset_update(self, index, preset):
        """Updates a specific export preset, and saves all presets.
        Arguments:
            index: Index of preset to update.
            preset: Preset data, List containing.
        """

        self.exports[index] = preset
        self.export_preset_write()

    def export_preset_new(self):
        """Create a new blank export preset."""

        preset = {'export': 'folder',
                  'ftp_address': '',
                  'ftp_user': '',
                  'ftp_password': '',
                  'ftp_passive': True,
                  'ftp_port': 21,
                  'name': 'Export Preset '+str(len(self.exports)+1),
                  'export_folder': '',
                  'create_subfolder': True,
                  'export_info': True,
                  'scale_image': False,
                  'scale_size': 1000,
                  'scale_size_to': 'long',
                  'jpeg_quality': 90,
                  'watermark_image': '',
                  'watermark': False,
                  'watermark_opacity': 33,
                  'watermark_horizontal': 90,
                  'watermark_vertical': 10,
                  'watermark_size': 25,
                  'ignore_tags': [],
                  'export_videos': False}
        self.exports.append(preset)

    def export_preset_write(self):
        """Saves all export presets to the config file."""

        configfile = ConfigParser(interpolation=None)
        for index, preset in enumerate(self.exports):
            section = str(index)
            configfile.add_section(section)
            configfile.set(section, 'name', preset['name'])
            configfile.set(section, 'export', preset['export'])
            configfile.set(section, 'ftp_address', preset['ftp_address'])
            configfile.set(section, 'ftp_user', preset['ftp_user'])
            configfile.set(section, 'ftp_password', preset['ftp_password'])
            configfile.set(section, 'ftp_passive', str(preset['ftp_passive']))
            configfile.set(section, 'ftp_port', str(preset['ftp_port']))
            configfile.set(section, 'export_folder', agnostic_path(preset['export_folder']))
            configfile.set(section, 'create_subfolder', str(preset['create_subfolder']))
            configfile.set(section, 'export_info', str(preset['export_info']))
            configfile.set(section, 'scale_image', str(preset['scale_image']))
            configfile.set(section, 'scale_size', str(preset['scale_size']))
            configfile.set(section, 'scale_size_to', preset['scale_size_to'])
            configfile.set(section, 'jpeg_quality', str(preset['jpeg_quality']))
            configfile.set(section, 'watermark', str(preset['watermark']))
            configfile.set(section, 'watermark_image', agnostic_path(preset['watermark_image']))
            configfile.set(section, 'watermark_opacity', str(preset['watermark_opacity']))
            configfile.set(section, 'watermark_horizontal', str(preset['watermark_horizontal']))
            configfile.set(section, 'watermark_vertical', str(preset['watermark_vertical']))
            configfile.set(section, 'watermark_size', str(preset['watermark_size']))
            configfile.set(section, 'ignore_tags', '|'.join(preset['ignore_tags']))
            configfile.set(section, 'export_videos', str(preset['export_videos']))

        with open(self.data_directory+os.path.sep+'exports.ini', 'w') as config:
            configfile.write(config)

    def export_preset_remove(self, index):
        """Deletes an export preset of a specifc index."""

        try:
            del self.exports[index]
        except:
            return
        self.export_preset_write()

    def import_preset_remove(self, index):
        """Deletes an import preset of a specifc index."""

        try:
            del self.imports[index]
        except:
            return
        self.import_preset_write()

    def import_preset_update(self, index, preset):
        """Overwrite a specific import preset, and save presets.
        Arguments:
            index: Integer, index of the preset to overwrite.
            preset: Dictionary, the new preset settings.
        """

        self.imports[index] = preset
        self.import_preset_write()

    def import_preset_new(self):
        """Create a new import preset with the default settings."""

        preset = {'title': 'Import Preset '+str(len(self.imports)+1), 'import_to': '', 'naming_method': naming_method_default, 'delete_originals': False, 'single_folder': False, 'import_from': []}
        self.imports.append(preset)

    def import_preset_write(self):
        """Saves all import presets to the config file."""

        configfile = ConfigParser(interpolation=None)
        for index, preset in enumerate(self.imports):
            section = str(index)
            configfile.add_section(section)
            configfile.set(section, 'title', preset['title'])
            configfile.set(section, 'import_to', agnostic_path(preset['import_to']))
            configfile.set(section, 'naming_method', preset['naming_method'])
            configfile.set(section, 'delete_originals', str(preset['delete_originals']))
            configfile.set(section, 'single_folder', str(preset['single_folder']))
            import_from = agnostic_path('|'.join(preset['import_from']))
            configfile.set(section, 'import_from', import_from)

        with open(self.data_directory+os.path.sep+'imports.ini', 'w') as config:
            configfile.write(config)

    def database_backup(self):
        """Makes a copy of the photos, folders and imported databases to a backup directory"""
        database_directory = self.data_directory # + os.path.sep + 'Databases'
        # database_backup_dir = os.path.join(database_directory, 'backup')
        # if not os.path.exists(database_backup_dir):
        #     os.makedirs(database_backup_dir)

        gomp_db = os.path.join(database_directory, 'gomp.db')
        gomp_db_backup = os.path.join(database_directory, 'gomp_backup.db')
        self.__overwrite_file(gomp_db, gomp_db_backup)

        # folders_db = os.path.join(database_directory, 'folders.db')
        # folders_db_backup = os.path.join(database_backup_dir, 'folders.db')
        # self.__overwrite_file(folders_db, folders_db_backup)

        # imported_db = os.path.join(database_directory, 'imported.db')
        # imported_db_backup = os.path.join(database_backup_dir, 'imported.db')
        # self.__overwrite_file(imported_db, imported_db_backup)

        # persons_db = os.path.join(database_directory, 'persons.db')
        # persons_db_backup = os.path.join(database_backup_dir, 'persons.db')
        # self.__overwrite_file(persons_db, persons_db_backup)

    def __overwrite_file(self, db, db_backup):
        if os.path.exists(db_backup):
            os.remove(db_backup)
        if os.path.exists(db):
            copyfile(db, db_backup)

    def database_restore(self):
        """Attempts to restore the backup databases"""

        self.close_settings()
        if self.database_scanning:
            self.cancel_database_import()
            self.scanningthread.join()
        #self.persons.close()
        #self.persons.join()
        self.__close_join_database()
        self.show_database_restore()

    def database_restore_process(self):
        database_directory = self.data_directory + os.path.sep + 'Databases'
        gomp_db = os.path.join(database_directory, 'gomp.db')
        gomp_db_backup = os.path.join(database_directory, 'gomp_backup.db')

        if not os.path.exists(database_directory):
            return "Backup does not exist"

        files = [gomp_db_backup]
        for file in files:
            if not os.path.exists(file):
                return "Backup does not exist"
        try:
            os.remove(gomp_db)
            copyfile(gomp_db_backup, gomp_db)
        except:
            return "Could not copy backups"
        return True

    def setup_database(self, restore=False):
        """Set up various databases, create if needed."""

        database_directory = self.data_directory
        if not os.path.exists(database_directory):
            os.makedirs(database_directory)

        try:
            self.database_path = 'sqlite:///'+os.path.join(database_directory, 'gomp.db')
            engine = create_engine(self.database_path, echo=True)
            create_database(engine)
            Session = sessionmaker(bind=engine)
            self.session = Session()

        except Exception as e:
            print(e)
            raise ValueError(e)

        if not restore and self.config.getboolean("Settings", "backupdatabase"):
            self.database_backup()

    def left_panel_width(self):
        """Returns the saved width for the left panel.
        Returns: Width of the panel in pixels.
        """

        minpanelsize = (self.button_scale / 2)
        leftpanel = float(self.config.get('Settings', 'leftpanel'))
        leftpanelsize = (leftpanel * Window.width)
        maxwidth = Window.width * 0.4
        if leftpanelsize > minpanelsize and leftpanelsize < maxwidth:
            panelwidth = leftpanelsize
        elif leftpanelsize >= maxwidth:
            panelwidth = maxwidth
        else:
            panelwidth = minpanelsize
        panelwidth = int(panelwidth)
        return panelwidth

    def right_panel_width(self):
        """Returns the saved width for the right panel.
        Returns: Width of the panel in pixels.
        """

        minpanelsize = (self.button_scale / 2)
        rightpanel = float(self.config.get('Settings', 'rightpanel'))
        rightpanelsize = (rightpanel * Window.width)
        maxwidth = Window.width * 0.4
        if rightpanelsize >= minpanelsize and rightpanelsize <= maxwidth:
            return rightpanelsize
        if rightpanelsize >= maxwidth:
            return maxwidth
        else:
            return minpanelsize

    def get_application_config(self, **kwargs):
        if platform == 'win':
            self.data_directory = os.getenv('APPDATA') + os.path.sep + "Snu Photo Manager"
            if not os.path.isdir(self.data_directory):
                os.makedirs(self.data_directory)
        elif platform == 'linux':
            self.data_directory = os.path.expanduser('~') + os.path.sep + ".snuphotomanager"
            if not os.path.isdir(self.data_directory):
                os.makedirs(self.data_directory)
        elif platform == 'macosx':
            self.data_directory = os.path.expanduser('~') + os.path.sep + ".snuphotomanager"
            if not os.path.isdir(self.data_directory):
                os.makedirs(self.data_directory)
        elif platform == 'android':
            self.data_directory = self.user_data_dir
        else:
            self.data_directory = os.path.sep
        self.app_location = os.path.realpath(self.directory)
        # __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        #__location__ = os.path.realpath(sys.path[0])
        #if __location__.endswith('.zip'):
        #    __location__ = os.path.dirname(__location__)
        config_file = os.path.realpath(os.path.join(self.data_directory, "snuphotomanager.ini"))
        print("Config File: "+config_file)
        return config_file

    def load_encoding_presets(self):
        """Loads the video encoding presets from the 'encoding_presets.ini' file."""

        try:
            configfile = ConfigParser(interpolation=None)
            configfile.read(os.path.join(self.app_location, '../data/encoding_presets.ini'))
            preset_names = configfile.sections()
            for preset_name in preset_names:
                if preset_name == 'Automatic':
                    preset = {'name': 'Automatic',
                              'file_format': 'auto',
                              'video_codec': '',
                              'audio_codec': '',
                              'resize': False,
                              'width': '',
                              'height': '',
                              'video_bitrate': '',
                              'audio_bitrate': '',
                              'encoding_speed': '',
                              'deinterlace': False,
                              'command_line': ''}
                    self.encoding_presets.append(preset)
                try:
                    preset = {'name': preset_name,
                              'file_format': configfile.get(preset_name, 'file_format'),
                              'video_codec': configfile.get(preset_name, 'video_codec'),
                              'audio_codec': configfile.get(preset_name, 'audio_codec'),
                              'resize': to_bool(configfile.get(preset_name, 'resize')),
                              'width': configfile.get(preset_name, 'width'),
                              'height': configfile.get(preset_name, 'height'),
                              'video_bitrate': configfile.get(preset_name, 'video_bitrate'),
                              'audio_bitrate': configfile.get(preset_name, 'audio_bitrate'),
                              'encoding_speed': configfile.get(preset_name, 'encoding_speed'),
                              'deinterlace': to_bool(configfile.get(preset_name, 'deinterlace')),
                              'command_line': configfile.get(preset_name, 'command_line')}
                    self.encoding_presets.append(preset)
                except:
                    pass
        except:
            pass
        try:
            self.selected_encoder_preset = self.config.get("Presets", "selected_preset")
        except:
            self.selected_encoder_preset = self.encoding_presets[0]['name']

    def save_encoding_preset(self):
        self.config.set("Presets", "selected_preset", self.selected_encoder_preset)

    def rescale_interface(self, force=False):
        if self.last_width == 0:
            first_change = True
        else:
            first_change = False
        if Window.width != self.last_width or force:
            self.popup_x = int(Window.width * .75)
            self.last_width = Window.width
            if first_change and desktop:
                #kivy bugs out on the first refresh on kivy older than 1.11, so skip it if on that version
                if kivy_version_primary <= 1 and kivy_version_secondary < 11:
                    return
            if desktop:
                button_multiplier = 1
            else:
                button_multiplier = 2
            self.button_scale = int((Window.height / interface_multiplier) * int(self.config.get("Settings", "buttonsize")) / 100) * button_multiplier
            self.padding = self.button_scale / 4
            self.text_scale = int((self.button_scale / 3) * int(self.config.get("Settings", "textsize")) / 100)
            #Clock.schedule_once(self.show_database)  Yvan

    def set_transition(self):
        if self.animations:
            self.screen_manager.transition = SlideTransition()
        else:
            self.screen_manager.transition = NoTransition()

    def build(self):
        """Called when the app starts.  Load and set up all variables, data, and screen."""

        self.theme = Theme(self)
        self.theme.default()
        Window.clearcolor = list(self.theme.background)

        if int(self.config.get("Settings", "buttonsize")) < 50:
            self.config.set("Settings", "buttonsize", 50)
        if int(self.config.get("Settings", "textsize")) < 50:
            self.config.set("Settings", "textsize", 50)
        if int(self.config.get("Settings", "thumbsize")) < 100:
            self.config.set("Settings", "thumbsize", 100)

        self.thumbsize = int(self.config.get("Settings", "thumbsize"))
        self.simple_interface = to_bool(self.config.get("Settings", "simpleinterface"))
        #Load data

        about_file = open(os.path.join(self.app_location, 'about.txt'), 'r')
        self.about_text = about_file.read()
        about_file.close()
        self.program_import()  #Load external program presets
        self.setup_import_presets()  #Load import presets
        self.setup_export_presets()  #Load export presets
        self.setup_database()  #Import or set up databases
        self.load_encoding_presets()
        self.set_single_database()

        #Set up widgets
        self.main_layout = MainWindow()
        self.drag_image = PhotoDrag()
        self.drag_treenode = TreenodeDrag()

        #Set up screen
        self.screen_manager = ScreenManager()
        self.animations = to_bool(self.config.get("Settings", "animations"))
        self.set_transition()
        self.main_layout.add_widget(self.screen_manager)
        viewtype = 'None'
        viewtarget = ''
        viewdisplayable = False
        if self.config.getboolean("Settings", "rememberview"):
            config_viewtype = self.config.get("Settings", "viewtype")
            if config_viewtype:
                viewtype = config_viewtype
                viewtarget = self.config.get("Settings", "viewtarget")
                viewdisplayable = to_bool(self.config.get("Settings", "viewdisplayable"))
        self.database_screen = ScreenDatabase(name='screenDatabase', type=viewtype, selected=viewtarget, displayable=viewdisplayable)
        self.screen_manager.add_widget(self.database_screen)  # yvan
        self.database_restore_screen = ScreenDatabaseRestore(name='database_restore')

        #Set up keyboard catchers
        Window.bind(on_key_down=self.key_down)
        Window.bind(on_key_up=self.key_up)
        if self.config.getboolean("Settings", "rescanstartup"):
            self.database_import()

        inspector.create_inspector(Window,App.get_running_app)

        return self.main_layout

    def key_down(self, key, scancode=None, *_):
        """Intercepts various key presses and sends commands to the current screen."""
        del key
        if scancode == 303 or scancode == 304:
            #shift keys
            self.shift_pressed = True

    def key_up(self, key, scancode=None, *_):
        """Checks for the shift key released."""

        del key
        if scancode == 303 or scancode == 304:
            self.shift_pressed = False





    def delete_folder_original(self, folder):
        """Delete all original unedited files in a given folder"""

        photos = self.Photo.by_folder(folder)
        deleted_photos = []
        for photoinfo in photos:
            original_file = local_path(photoinfo[10])
            deleted = self.delete_file(original_file)
            if deleted is True:
                deleted_photos.append(photoinfo)
        return deleted_photos

    def delete_photo_original(self, photoinfo):
        """Delete the original unedited file.
        Argument:
            photoinfo: List, photoinfo object.
        """

        original_file = local_path(photoinfo[10])
        if os.path.isfile(original_file):
            deleted = self.delete_file(original_file)
            if deleted is not True:
                return False, 'Could not delete original file: '+str(deleted)
        else:
            return False, 'Could not find original file'
        return True, "Deleted original file"

    def delete_file(self, filepath):
        """Attempt to delete a file using send2trash.
        Returns:
            True if file was deleted
            False if file could not be deleted
        """

        try:
            send2trash(filepath)
            #os.remove(filepath)
        except Exception as ex:
            return ex
        return True


    def move_files(self, photo_paths, move_to):
        """Move files from one folder to another.  Will keep files in the same screenDatabase-relative path as they are in.
        Arguments:
            photo_paths: List of Strings, a screenDatabase-relative path to each file being moved.
            move_to: String, a screenDatabase-relative path to the folder the files should be moved to.
        """

        update_folders = []
        moved = 0
        folder = self.session.query(Folder).filter_by(name=move_to).first()
        for photo in photo_paths:
            photo.folder = folder
            self.session.commit()
            moved = moved + 1

            # photo_info = self.Photo.exist(fullpath)
            # if photo_info:
            #     new_path = os.path.join(photo_info[2], move_to)
            #     try:
            #         if not os.path.isdir(new_path):
            #             os.makedirs(new_path)
            #     except:
            #         self.popup_message(text='Error: Could Not Create Folder', title='Error')
            #         break
            #     photo_path = os.path.join(photo_info[2], photo_info[0])
            #     current_folder, current_file = os.path.split(photo_path)
            #     new_photo_path = os.path.join(new_path, current_file)
            #     new_fullpath = os.path.join(move_to, current_file)
            #     backup_path = photo_info[10]
            #     if os.path.exists(backup_path):
            #         new_backup_path = os.path.join(new_path, '.originals')
            #         new_backup_file = os.path.join(new_backup_path, current_file)
            #         try:
            #             os.makedirs(new_backup_path)
            #             os.rename(backup_path, new_backup_file)
            #         except:
            #             self.popup_message(text='Error: Could Not Move Backup File', title='Error')
            #             break
            #         if not os.path.exists(new_backup_file):
            #             self.popup_message(text='Error: Could Not Move Backup File', title='Error')
            #             break
            #         photo_info[10] = new_backup_file
            #     if os.path.exists(photo_path):
            #         try:
            #             os.rename(photo_path, new_photo_path)
            #         except:
            #             self.popup_message(text='Error: Could Not Move File', title='Error')
            #             break
            #         if not os.path.exists(new_photo_path):
            #             self.popup_message(text='Error: Could Not Move File', title='Error')
            #             break
            #
            #         self.Photo.update(photo_info)
            #         self.Photo.rename(fullpath, new_fullpath, move_to)
            #         update_folders.append(photo_info[1])
        if moved:
            self.message("Moved "+str(moved)+" files.")
        # update_folders.append(move_to)
        # self.update_photoinfo(folders=update_folders)

    def move_folder(self, folder, move_to, rename=False):
        """Move a folder and all files in it to another location.  Also updates screenDatabase entries.
        Arguments:
            folder: String, the path of the folder to move.
            move_to: String, the path to place the folder inside of.
            rename: Set to a String to rename the folder while it is moved.  Defaults to False.
        """

        error_message = ''
        databases = self.get_database_directories()
        for database in databases:
            move_from_folder = os.path.join(database, folder)
            move_to_folder = os.path.join(database, move_to)
            try:
                if rename:
                    moving_folder = rename
                else:
                    moving_folder = os.path.split(folder)[1]
                if not os.path.isdir(os.path.join(move_to_folder, moving_folder)):
                    if os.path.isdir(move_from_folder):
                        folders = []
                        folders.append('')
                        found_folders = list_folders(move_from_folder)
                        for found_folder in found_folders:
                            folders.append(os.path.join(found_folder))
                        if rename:
                            move(move_from_folder, os.path.join(move_to_folder, rename))
                        else:
                            move(move_from_folder, move_to_folder)
                        #Update screenDatabase entries of all photos in folder
                        update_folders = []
                        for path in folders:
                            if path:
                                new_folder = os.path.join(os.path.join(move_to, moving_folder), path)
                                photo_path = os.path.join(folder, path)
                            else:
                                new_folder = os.path.join(move_to, moving_folder)
                                photo_path = folder
                            # self.database_folder_rename(photo_path, new_folder)
                            photos = self.Photo.by_folder(photo_path)
                            update_folders.append(photo_path)
                            for photo in photos:
                                if photo[2] == database:
                                    filename = os.path.basename(photo[0])
                                    new_fullpath = os.path.join(new_folder, filename)
                                    self.Photo.rename(photo[0], new_fullpath, new_folder, dontcommit=True)
                        #self.update_photoinfo(folders=update_folders)
                else:
                    raise ValueError
            except Exception as e:
                if rename:
                    error_message = 'Unable To Rename Folder, '+str(e)
                else:
                    error_message = 'Unable To Move Folder, '+str(e)
                self.popup_message(text=error_message, title='Error:')
        if not error_message:
            if rename:
                self.message("Renamed the folder '"+folder+"' to '"+rename+"'")
            else:
                if not move_to:
                    self.message("Moved the folder '" + folder + "' into Root")
                else:
                    self.message("Moved the folder '"+folder+"' into '"+move_to+"'")
        self.Photo.commit()


    def database_imported_exists(self, fullpath):
        """Get photo data if it is in the imported screenDatabase.
        Argument:
            fullpath: String, screenDatabase-relative path to the photo.
        Returns:
            List of photoinfo if photo found, None if not found.
        """
        self.Photo.find_by_fullpath(fullpath)


    def null_image(self):
        """Returns a minimum photoinfo list pointing to 'null.jpg'.
        Returns: List, a photoinfo object.
        """

        return ['data/null.jpg', '', '', 0, 0, 'data/null.jpg', 0, 0, '', 0, 'data/null.jpg', '', 0, 1]

    def database_clean(self, deep=False):
        """Clean the databases of redundant or missing data.
        Argument:
            deep: Boolean. If True, will remove all files that are currently not found.
        """

        self.Photo.clean(deep)

        Clock.schedule_once(lambda *dt: self.screen_manager.current_screen.on_enter())


    def database_rescan(self):
        """Calls database_import."""

        self.database_import()


    def cancel_database_import(self, *_):
        """Signals the screenDatabase scanning thread to stop."""

        self.cancel_scanning = True

    def database_import(self):
        """Begins the screenDatabase scanning process.
        Scans the screenDatabase folders for new files and adds them.
        Open the popup progress dialog, and start the scanning thread.
        """

        if self.database_scanning:
            return
        self.cancel_scanning = False
        self.scanningthread = threading.Thread(target=self.database_import_files)
        self.scanningthread.start()

    def get_database_directories(self):
        """Gets the current screenDatabase directories.
        Returns: List of Strings of the paths to each screenDatabase.
        """

        directories = self.config.get('Database Directories', 'paths')
        directories = local_path(directories)
        if directories:
            databases = directories.split(';')
        else:
            databases = []
        databases_cleaned = []
        for database in databases:
            if database:
                databases_cleaned.append(database)
        return databases_cleaned

    def list_files(self, folder):
        """Function that returns a list of every nested file within a folder.
        Argument:
            folder: The folder name to look in
        Returns: A list of file lists, each list containing:
            Full path to the file, relative to the root directory.
            Root directory for all files.
        """

        file_list = []
        firstroot = False
        walk = os.walk
        for root, dirs, files in walk(folder, topdown=True):
            if self.cancel_scanning:
                return []
            if not firstroot:
                firstroot = root
            filefolder = os.path.relpath(root, firstroot)
            if filefolder == '.':
                filefolder = ''
            for file in files:
                if self.cancel_scanning:
                    return []
                file_list.append([os.path.join(filefolder, file), firstroot])
        return file_list

    def database_find_file(self, file_info):
        #search the screenDatabase for a file that has been moved to a new directory, returns the updated info or None if not found.
        filepath, filename = os.path.split(file_info[0])
        old_photos = self.photos.select('SELECT * FROM photos WHERE FullPath LIKE ?', ('%'+filename+'%',))
        if old_photos:
            possible_matches = []
            old_photos = list(old_photos)
            for photo in old_photos:
                #check if photo still exists, ignore if it does
                photo_path = os.path.join(local_path(photo[2]), local_path(photo[0]))
                if not os.path.exists(photo_path):
                    possible_matches.append(photo)
            #return first match
            if possible_matches:
                return possible_matches[0]
        return None

    def database_import_files(self):
        """Database scanning thread, checks for new files in the screenDatabase directories and adds them to the screenDatabase."""

        self.database_scanning = True
        self.database_update_text = 'Rescanning Database, Building Folder List'
        databases = self.get_database_directories()
        update_folders = []

        #Get the file list
        files = []
        for directory in databases:
            if self.cancel_scanning:
                break
            files = files + self.list_files(directory)

        total = len(files)
        self.database_update_text = 'Rescanning Database (5%)'

        #Iterate all files, check if in screenDatabase, add if needed.
        for index, file_info in enumerate(files):
            if self.cancel_scanning:
                break
            extension = os.path.splitext(file_info[0])[1].lower()
            if extension in imagetypes or extension in movietypes:
                exists = self.Photo.exist(file_info[0])
                if not exists:
                    #photo not in screenDatabase, add it or ceck if moved
                    raise ValueError('must verify next function')
                    #file_info = get_file_info(file_info)
                    found_file = self.database_find_file(file_info)
                    if found_file:
                        found_file = agnostic_photoinfo(list(found_file))
                        self.Photo.rename(found_file[0], file_info[0], file_info[1], dontcommit=True)
                        update_folders.append(found_file[1])
                        update_folders.append(file_info[1])
                    else:
                        self.Photo.add(file_info)
                        update_folders.append(file_info[1])
                else:
                    #photo is already in the screenDatabase
                    #check modified date to see if it needs to be updated and look for duplicates
                    refreshed = self.refresh_photo(file_info[0], no_photoinfo=True, data=exists, skip_isfile=True)
                    if refreshed:
                        update_folders.append(refreshed[1])

            self.database_update_text = 'Rescanning Database ('+str(int(90*(float(index+1)/float(total))))+'%)'

        #Update folders
        folders = self.Folder.all()
        for folder in folders:
            if self.cancel_scanning:
                break
            exists = self.Folder.exist(folder)
            if not exists:
                folderinfo = get_folder_info(folder, databases)
                self.Folder.insert(folderinfo)
                update_folders.append(folderinfo[0])
        self.update_photoinfo(folders=folders)
        self.Photo.commit()

        #Clean up screenDatabase
        if not self.cancel_scanning:
            self.database_update_text = 'Cleaning Database...'
            self.database_clean()
            self.database_update_text = "Database scanned "+str(total)+" files"

        self.update_photoinfo(folders=update_folders)
        if self.cancel_scanning:
            self.database_update_text = "Canceled screenDatabase update."
        self.database_scanning = False
        Clock.schedule_once(self.clear_database_update_text, 20)
        if self.screen_manager.current == 'screenDatabase':
            self.database_screen.update_folders = True
            Clock.schedule_once(self.database_screen.update_treeview)

    def show_database(self, *_):
        """Switch to the screenDatabase screen layout."""
        import datetime

        print(datetime.datetime.now().time(),"show_database called")

        self.clear_drags()
        if 'screenDatabase' not in self.screen_manager.screen_names:
            self.screen_manager.add_widget(self.database_screen)
        if self.animations:
            self.screen_manager.transition.direction = 'right'
        self.screen_manager.current = 'screenDatabase'

    def show_database_restore(self):
        """Switch to the screenDatabase restoring screen layout."""

        self.clear_drags()
        if 'database_restore' not in self.screen_manager.screen_names:
            self.screen_manager.add_widget(self.database_restore_screen)
        self.screen_manager.current = 'database_restore'

    def show_theme(self):
        """Switch to the theme editor screen layout."""

        self.clear_drags()
        if 'theme' not in self.screen_manager.screen_names:
            from screens.ScreenTheme import ScreenTheme
            self.screen_manager.add_widget(ScreenTheme(name='theme'))
        if self.animations:
            self.screen_manager.transition.direction = 'left'
        self.screen_manager.current = 'theme'

    def show_collage(self):
        """Switch to the create collage screen layout.
        """

        self.clear_drags()
        if 'collage' not in self.screen_manager.screen_names:
            from screens.screencollage import ScreenCollage
            self.screen_manager.add_widget(ScreenCollage(name='collage'))
        self.type = self.database_screen.type
        self.target = self.database_screen.selected
        if self.animations:
            self.screen_manager.transition.direction = 'left'
        self.screen_manager.current = 'collage'

    def show_album(self, button=None):
        """Switch to the album screen layout.
        Argument:
            button: Optional, the widget that called this function. Allows the function to get a specific album to view.
        """

        self.clear_drags()
        if 'album' not in self.screen_manager.screen_names:
            from screens.screenAlbum import ScreenAlbum
            self.album_screen = ScreenAlbum(name='album')
            self.screen_manager.add_widget(self.album_screen)
        if self.animations:
            self.screen_manager.transition.direction = 'left'
        if button:
            if button.type != 'None':
                if not button.folder:
                    self.fullpath = ''
                    self.target = button.target
                    self.photo = ''
                    self.type = button.type
                    self.screen_manager.current = 'album'
                else:
                    self.fullpath = button.fullpath
                    self.target = button.target
                    self.photo = os.path.join(button.database_folder, button.fullpath)
                    self.type = button.type
                    self.screen_manager.current = 'album'
        else:
            self.screen_manager.current = 'album'

    def show_import(self):
        """Switch to the import select screen layout."""

        self.clear_drags()
        if 'import' not in self.screen_manager.screen_names:
            from screens.ScreenImportPreset import ScreenImportPreset
            from screens.ScreenImporting import ScreenImporting
            self.importing_screen = ScreenImporting(name='importing')
            self.screen_manager.add_widget(ScreenImportPreset(name='import'))
        if self.animations:
            self.screen_manager.transition.direction = 'left'
        self.screen_manager.current = 'import'

    def show_importing(self):
        """Switch to the photo import screen layout."""

        self.clear_drags()
        if 'importing' not in self.screen_manager.screen_names:
            self.screen_manager.add_widget(self.importing_screen)
        if self.animations:
            self.screen_manager.transition.direction = 'left'
        self.screen_manager.current = 'importing'

    def show_export(self):
        """Switch to the photo export screen layout."""

        self.clear_drags()
        if 'export' not in self.screen_manager.screen_names:
            from screens.ScreenExporting import ScreenExporting
            self.screen_manager.add_widget(ScreenExporting(name='export'))
        if self.animations:
            self.screen_manager.transition.direction = 'left'
        self.screen_manager.current = 'export'

    def show_transfer(self):
        """Switches to the screenDatabase transfer screen layout"""

        self.clear_drags()
        if 'transfer' not in self.screen_manager.screen_names:
            self.screen_manager.add_widget(ScreenDatabaseTransfer(name='transfer'))
        if self.animations:
            self.screen_manager.transition.direction = 'left'
        self.screen_manager.current = 'transfer'

    def popup_message(self, text, title='Notification'):
        """Creates a simple 'ok' popup dialog.
        Arguments:
            text: String, text that the dialog will display
            title: String, the dialog window title.
        """

        app = App.get_running_app()
        content = MessagePopup(text=text)
        self.popup = NormalPopup(title=title, content=content, size_hint=(None, None), size=(app.popup_x, app.button_scale * 4))
        self.popup.open()

    def clear_drags(self):
        """Removes the drag-n-drop widgets and copy popups."""

        self.close_bubble()
        self.main_layout.remove_widget(self.drag_treenode)
        self.main_layout.remove_widget(self.drag_image)

    def drag(self, drag_object, mode, position, image=None, offset=list([0, 0]), fullpath=''):
        """Updates the drag-n-drop widget for a standard photo.
        Arguments:
            drag_object: The widget that is being dragged.
            mode: String, what is being done with the drag: 'start', 'end' or 'move'.
            position: The position (x, y) the drag widget should be at in window coordinates.
            image: Needs to be provided if mode is 'start', the image the drag widget should have.
            offset: Needs to be provided if mode is 'start',
                    offset where the drag began, to make the image be placed in the correct location.
            fullpath: Needs to be provided if the mode is 'start',
                      String, the screenDatabase-relative path of the image being dragged.
        """

        if mode == 'end':
            self.main_layout.remove_widget(self.drag_image)
            self.screen_manager.current_screen.drop_widget(self.drag_image.fullpath, position, dropped_type='file', aspect=self.drag_image.image_ratio)

        elif mode == 'start':
            orientation = drag_object.photo_orientation
            if orientation == 3 or orientation == 4:
                angle = 180
            elif orientation == 5 or orientation == 6:
                angle = 270
            elif orientation == 7 or orientation == 8:
                angle = 90
            else:
                angle = 0
            self.drag_image.width = drag_object.children[0].width
            self.drag_image.height = drag_object.height
            self.drag_image.angle = angle
            self.drag_image.offset = offset
            self.main_layout.remove_widget(self.drag_image)
            self.drag_image.pos = (position[0]-offset[0], position[1]-offset[1])
            self.drag_image.texture = image.texture
            self.drag_image.fullpath = fullpath
            self.main_layout.add_widget(self.drag_image)

        else:  #mode == 'move'
            self.drag_image.pos = (position[0]-self.drag_image.offset[0], position[1]-self.drag_image.offset[1])

    def drag_treeview(self, drag_object, mode, position, offset=list([0, 0])):
        """Updates the drag-n-drop widget for a treeview folder.
        Arguments:
            drag_object: The widget that is being dragged.
            mode: String, what is being done with the drag: 'start', 'end' or 'move'.
            position: The position (x, y) the drag widget should be at in window coordinates.
            offset: Needs to be provided if mode is 'start',
                    offset where the drag began, to make the image be placed in the correct location.
        """

        if mode == 'end':
            self.main_layout.remove_widget(self.drag_treenode)
            self.screen_manager.current_screen.drop_widget(drag_object.fullpath, position, dropped_type=drag_object.droptype, aspect=1)

        elif mode == 'start':
            self.drag_treenode.offset = offset
            self.main_layout.remove_widget(self.drag_treenode)
            self.drag_treenode.text = drag_object.folder_name
            if drag_object.subtext:
                self.drag_treenode.height = int(self.button_scale * 1.5)
                self.drag_treenode.subtext = drag_object.subtext
                self.drag_treenode.ids['subtext'].height = int(self.button_scale * 0.5)
            else:
                self.drag_treenode.subtext = ''
                self.drag_treenode.ids['subtext'].height = 0
                self.drag_treenode.height = int(self.button_scale * 1)
            self.drag_treenode.width = drag_object.width
            self.drag_treenode.pos = (position[0]-offset[0], position[1]-offset[1])
            self.main_layout.add_widget(self.drag_treenode)

        else:
            self.drag_treenode.pos = (position[0]-self.drag_treenode.offset[0], position[1]-self.drag_treenode.offset[1])


    def remove_unallowed_characters(self, string, *_):
        """Checks a person input string, removes non-allowed characters and sets to lower-case.
        Arguments:
            string: String to replace.
        Returns: A string.
        """

        return "".join(i for i in string if i not in "#%&*{}\\/:?<>+|\"=][;,").lower()


    def new_description(self, description_editor, root):
        """Update the description of a folder or album.
        Arguments:
            description_editor: Widget, the text input object that was edited.
            root: The screen that owns the text input widget.  Has information about the folder or album being edited.
        """

        if not description_editor.focus:
            folder = root.selected_item
            if root.type == 'Folder':
                folder.description = description_editor.text
                self.session.commit()

    def new_title(self, title_editor, root):
        """Update the title of a folder or album.
        Arguments:
            title_editor: Widget, the text input object that was edited.
            root: The screen that owns the text input widget.  Has information about the folder or album being edited.
        """

        if not title_editor.focus:
            folder = root.selected_item
            if root.type == 'Folder':
                folder.title = title_editor.text
                self.session.commit()

    def edit_add_watermark(self, imagedata, watermark_image, watermark_opacity, watermark_horizontal, watermark_vertical, watermark_size):
        """Adds a watermark overlay to an image

        imagedata - the image to apply the watermark to, a PIL image object
        watermark_image - a string with the watermark filepath
        watermark_opacity - a percentage (0-100) describing how opaque the watermark will be
        watermark_horizontal - a percentage (0-100) describing the horizontal position of the watermark,
            with 0 being all the way on the left side, 100 being all the way on the right side.
            The watermark will never be partially off of the original image
        watermark_vertical - a percentage (0-100) describing the vertical position of the watermark
        watermark_size - a percentage (0-100) describing the size of the watermark as its horizontal size relates
            to the original image - 50% will result in a watermark that is half the width of the original image.

        Returns a PIL image object
        """

        image_size = imagedata.size
        watermark = Image.open(watermark_image)
        watermark_size_pixels = watermark.size
        watermark_width, watermark_height = watermark_size_pixels
        watermark_ratio = watermark_width/watermark_height
        new_watermark_width = int(round(image_size[0]*(watermark_size/100)))
        new_watermark_height = int(round(new_watermark_width/watermark_ratio))
        watermark = watermark.resize((new_watermark_width, new_watermark_height), 3)
        watermark_x = int(round((image_size[0]-new_watermark_width)*(watermark_horizontal/100)))
        watermark_y = image_size[1] - new_watermark_height - int(round((image_size[1]-new_watermark_height)*(watermark_vertical/100)))
        if watermark.mode == 'RGBA':
            watermark_alpha = watermark.split()[3]
        else:
            watermark_alpha = watermark.convert('L')
        enhancer = ImageEnhance.Brightness(watermark_alpha)
        watermark_alpha = enhancer.enhance(watermark_opacity/100)
        imagedata.paste(watermark, (watermark_x, watermark_y), watermark_alpha)
        return imagedata

    def edit_fix_orientation(self, imagedata, orientation):
        """Rotates an image to the correct orientation

        imagedata - the image to apply the rotation to, a PIL image object
        orientation - jpeg exif orientation value

        Returns a PIL image object
        """

        if orientation in [2, 4, 5, 7]:
            mirror = True
        else:
            mirror = False
        if orientation == 3 or orientation == 4:
            angle = 180
            method = 3
        elif orientation == 5 or orientation == 6:
            angle = 270
            method = 4
        elif orientation == 7 or orientation == 8:
            angle = 90
            method = 2
        else:
            angle = 0
            method = False
        if angle:
            #imagedata = imagedata.rotate(angle)
            imagedata = imagedata.transpose(method=method)
        if mirror:
            imagedata = imagedata.transpose(method=0)
        return imagedata

    def edit_scale_image(self, imagedata, scale_size, scale_size_to):
        """Scales an image based on a side length while maintaining aspect ratio.

        imagedata - the image to apply the scaling to, a PIL image object
        scale_size - the target edge length in pixels
        scale_size_to - scaling mode, set to one of ('width', 'height', 'short', 'long')
            width - scales the image so the width matches scale_size
            height - scales the image so the height matches scale_size
            short - scales the image so the shorter side matches scale_size
            long - scales the image so the longer side matches scale_size

        Returns a PIL image object
        """

        original_size = imagedata.size
        ratio = original_size[0]/original_size[1]
        if scale_size_to == 'width':
            new_size = (scale_size, int(round(scale_size/ratio)))
        elif scale_size_to == 'height':
            new_size = (int(round(scale_size*ratio)), scale_size)
        elif scale_size_to == 'short':
            if original_size[0] > original_size[1]:
                new_size = (int(round(scale_size*ratio)), scale_size)
            else:
                new_size = (scale_size, int(round(scale_size/ratio)))
        else:
            if original_size[0] > original_size[1]:
                new_size = (scale_size, int(round(scale_size/ratio)))
            else:
                new_size = (int(round(scale_size*ratio)), scale_size)
        return imagedata.resize(new_size, 3)