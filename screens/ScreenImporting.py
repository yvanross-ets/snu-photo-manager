import datetime
import os
import threading
import time
from shutil import copy2
from shutil import copyfile
import sqlite3

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, ListProperty, NumericProperty
from kivy.uix.screenmanager import Screen
from models.FileInfo import FileInfo
from generalcommands import list_files, format_size, naming
from generalconstants import imagetypes, movietypes
from generalElements.popups.ScanningPopup import ScanningPopup
from generalElements.popups.InputPopup import InputPopup
from generalElements.popups.NormalPopup import NormalPopup
from generalElements.treeviews.TreeViewButton import TreeViewButton
from generalElements.photos.PhotoRecycleThumbWide import PhotoRecycleThumbWide  # used in builder
from screens.ScreenImportPreset import disk_usage
from kivy.lang.builder import Builder
from models.Folder import Folder
from models.Photo import Photo


Builder.load_string("""
<ScreenImporting>:
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
            MediumBufferX:
            NormalButton:
                text: 'Import Photos'
                on_release: root.finalize_import()
            MediumBufferX:
            ShortLabel:
                id: totalSize
                text: ''
            MediumBufferX:
            NormalToggle:
                state: 'down' if root.delete_originals == True else 'normal'
                text: 'Delete Original Photos' if root.delete_originals else 'Dont Delete Original Photos'
                on_press: root.set_delete_originals(self.state)
            HeaderLabel:
                text: 'Import Photos'
            InfoLabel:
            DatabaseLabel:
            SettingsButton:
        MainArea:
            orientation: 'horizontal'
            SplitterPanelLeft:
                id: leftpanel
                #width: app.leftpanel_width
                BoxLayout:
                    orientation: 'vertical'
                    Header:
                        size_hint_y: None
                        height: app.button_scale
                        NormalLabel:
                            text: 'Folders:'
                        NormalButton:
                            text: 'Delete Folder'
                            on_release: root.delete_folder()
                        NormalButton:
                            text: 'New Folder'
                            on_release: root.add_folder()
                    BoxLayout:
                        Scroller:
                            id: foldersContainer
                            do_scroll_x: True
                            NormalTreeView:
                                id: folders
            BoxLayout:
                orientation: 'vertical'
                Header:
                    ShortLabel:
                        text: 'Current Photos In:'
                    NormalLabel:
                        id: folderName
                        text: ''
                    LargeBufferX:
                    NormalButton:
                        text: 'Toggle Select'
                        on_release: root.toggle_select()
                    NormalButton:
                        id: deleteButton
                        text: 'Remove Selected'
                        disabled: True
                        on_release: root.delete()
                BoxLayout:
                    id: folderDetails
                    size_hint_y: None
                    height: (app.button_scale * 2)
                    orientation: 'horizontal'
                    BoxLayout:
                        orientation: 'vertical'
                        Header:
                            ShortLabel:
                                text: 'Title:'
                            NormalInput:
                                disabled: True
                                id: folderTitle
                                input_filter: app.remove_unallowed_characters
                                multiline: False
                                text: ''
                                on_text: root.new_title(self)
                        Label:
                    LargeBufferX:
                    Header:
                        height: (app.button_scale * 2)
                        BoxLayout:
                            size_hint_x: None
                            orientation: 'vertical'
                            ShortLabel:
                                text: 'Description:'
                            ShortLabel:
                        NormalInput:
                            disabled: True
                            id: folderDescription
                            height: (app.button_scale * 2)
                            input_filter: app.remove_unallowed_characters
                            multiline: True
                            text: ''
                            on_text: root.new_description(self)
                NormalRecycleView:
                    id: photosContainer
                    viewclass: 'PhotoRecycleThumbWide'
                    SelectableRecycleGridWide:
                        id: photos


""")

class ScreenImporting(Screen):
    """Screen layout for photo importing process.
    Displays photos from directories and lets you select which ones to import.
    """

    type = StringProperty('')
    selected = StringProperty('')
    import_to = StringProperty('')
    naming_method = StringProperty('')
    delete_originals = BooleanProperty(False)
    single_folder = BooleanProperty(False)
    import_from = ListProperty()
    popup = None
    import_photos = []
    duplicates = []
    photos = []
    folders = {}
    unsorted = []
    removed = []
    total_size = 0
    cancel_scanning = BooleanProperty(False)  #The importing process thread checks this and will stop if set to True.
    scanningpopup = None  #Popup dialog showing the importing process progress.
    scanningthread = None  #Importing files thread.
    popup_update_thread = None  #Updates the percentage and time index on scanning popup
    percent_completed = NumericProperty()
    start_time = NumericProperty()
    import_scanning = BooleanProperty(False)

    def get_selected_photos(self, fullpath=False):
        photos = self.ids['photos']
        selected_indexes = photos.selected_nodes
        photos_container = self.ids['photosContainer']
        selected_photos = []
        for selected in selected_indexes:
            if fullpath:
                selected_photos.append(photos_container.data[selected]['fullpath'])
            else:
                selected_photos.append(photos_container.data[selected]['photoinfo'])
        return selected_photos

    def dismiss_extra(self):
        """Cancels the import process if it is running"""

        if self.import_scanning:
            self.cancel_import()
            return True
        else:
            return False

    def date_to_folder(self, date):
        """Generates a string from a date in the format YYYYMMDD."""

        date_info = datetime.datetime.fromtimestamp(date)
        return str(date_info.year)+str(date_info.month).zfill(2)+str(date_info.day).zfill(2)

    def on_enter(self):
        """Called when the screen is entered.  Sets up variables, and scans the import folders."""

        app = App.get_running_app()
        self.ids['leftpanel'].width = app.left_panel_width()
        self.duplicates = []
        self.import_photos = []
        self.folders = {}
        self.unsorted = []
        self.removed = []
        self.total_size = 0
        self.import_scanning = False

        #Display message that folder scanning is in progress
        self.cancel_scanning = False
        self.scanningpopup = ScanningPopup(title='Scanning Import Folders...', auto_dismiss=False, size_hint=(None, None), size=(app.popup_x, app.button_scale * 4))
        self.scanningpopup.open()
        scanning_button = self.scanningpopup.ids['scanningButton']
        scanning_button.bind(on_release=self.cancel_import)

        self.percent_completed = 0
        self.scanningthread = threading.Thread(target=self.scan_folders)
        self.import_scanning = True
        self.scanningthread.start()
        self.start_time = time.time()

    def scan_folders(self, *_):
        """Function that scans the import folders for valid files to import
            and now really import files without using the interface to select file.
            Will import all files in directories.
        """
        app = App.get_running_app()

        main_thread_database_connection = app.Photo.database
        database = sqlite3.connect(app.database_path)
        photo_db = Photo(app,database)
        folder_db = Folder(app,database)


        current_timestamp = time.time()

        #Scan the folders
        for folder in self.import_from:
            if os.path.isdir(folder):
                files = list_files(folder)
                for file_info in files:
                    #update popup
                    if self.cancel_scanning:
                        self.scanning_canceled()
                        return
                    self.percent_completed = self.percent_completed + 1
                    if self.percent_completed > 100:
                        self.percent_completed = 0
                    self.scanningpopup.scanning_percentage = self.percent_completed

                    extension = os.path.splitext(file_info[0])[1].lower()
                    if extension in imagetypes or extension in movietypes:
                        file_info = FileInfo(file_info)

                        is_in_database = photo_db.exist(file_info.new_folder_with_filename())
                        if not is_in_database:
                            self.total_size = self.total_size+file_info.original_size[0]
                            self.import_photos.append(file_info)

        nbPhoto = len(self.import_photos)
        current_photo_index = 0
        app = App.get_running_app()
        for photo_info in self.import_photos:
            self.percent_completed = current_photo_index/nbPhoto * 100
            current_photo_index += 1
            print('---------')
            print(photo_info.old_full_filename())
            print(photo_info.new_folder_name())
            print(photo_info.new_full_filename(self.import_to))

            folder = folder_db.create_or_find(photo_info.new_folder_name())
            if not photo_db.exist(photo_info.new_folder_with_filename()):
                copyfile(photo_info.old_full_filename(), photo_info.new_full_filename(self.import_to))
                photo_db.insert(folder[Folder.ID],photo_info.new_full_filename(self.import_to),photo_info)



        self.scanningpopup.dismiss()
        self.scanningpopup = None
        self.scanningpopup = None
        self.import_scanning = False
        self.update_treeview()
        self.update_photolist()

        database.close()


    def scanning_canceled(self):
        app = App.get_running_app()
        app.message("Canceled import scanning.")
        self.scanningpopup.dismiss()
        self.scanningpopup = None
        self.import_scanning = False
        Clock.schedule_once(lambda *dt: app.show_database())

    def cancel_import(self, unknown=False):
        """Cancel the import process."""
        self.cancel_scanning = True

    def finalize_import(self):
        raise ValueError("should not call this function anymore because the load is done on preset selection")

        """Begin the final stage of the import - copying files."""
        app = App.get_running_app()

        #Create popup to show importing progress
        self.cancel_scanning = False
        self.scanningpopup = ScanningPopup(title='Importing Files', auto_dismiss=False, size_hint=(None, None), size=(app.popup_x, app.button_scale * 4))
        self.scanningpopup.open()
        scanning_button = self.scanningpopup.ids['scanningButton']
        scanning_button.bind(on_release=self.cancel_import)

        #Start importing thread
        self.percent_completed = 0
        self.scanningthread = threading.Thread(target=self.importing_process)
        self.import_scanning = True
        self.scanningthread.start()
        self.start_time = time.time()

    def importing_process(self):
        """Function that actually imports the files."""

        raise ValueError("should not call this function anymore because the load is done on preset selection")

        app = App.get_running_app()
        folders = self.folders
        import_to = self.import_to
        total_size = self.total_size
        imported_size = 0
        self.scanningpopup.scanning_text = "Importing "+format_size(total_size)+'  0%'
        imported_folders = []
        imported_files = 0
        failed_files = 0

        if disk_usage:
            free_space = disk_usage(import_to)[2]
            if total_size > free_space:
                self.scanningpopup.dismiss()
                self.scanningpopup = None
                app.message("Not enough free drive space! Cancelled import.")
                Clock.schedule_once(lambda *dt: app.show_import())

        #Scan folders
        for folder_path in folders:
            if self.cancel_scanning:
                break
            folder = folders[folder_path]
            folder_name = folder['name']
            if folder['photos']:
                if folder['naming']:
                    folder_name = naming(self.naming_method, title=folder['title'], year=folder['year'], month=folder['month'], day=folder['day'])
                photos = folder['photos']
                parent = folder['parent']
                if parent:
                    path_string = []
                    while parent:
                        newfolder = folders[parent]
                        newfolder_name = newfolder['name']
                        if newfolder['naming']:
                            newfolder_name = naming(self.naming_method, title=newfolder['title'], year=newfolder['year'], month=newfolder['month'], day=newfolder['day'])
                        path_string.append(newfolder_name)
                        parent = newfolder['parent']
                    for path in path_string:
                        folder_name = os.path.join(path, folder_name)
                folderinfo = [folder_name, folder['title'], folder['description']]
                path = os.path.join(import_to, folder_name)
                if not os.path.isdir(path):
                    os.makedirs(path)
                if not app.Folder.exist(folderinfo[0]):
                    app.Folder.insert(folderinfo)
                else:
                    if folderinfo[1]:
                        app.Folder.update_title(folderinfo[0], folderinfo[1]).commit()
                    if folderinfo[2]:
                        app.Folder.update_description(path,description)(folderinfo[0], folderinfo[2])

                #Scan and import photos in folder
                for photo in photos:
                    if self.cancel_scanning:
                        break
                    completed = (imported_size/total_size)
                    remaining = 1 - completed
                    self.percent_completed = 100*completed
                    self.scanningpopup.scanning_percentage = self.percent_completed

                    seconds_elapsed = time.time() - self.start_time
                    time_elapsed = '  Time: '+str(datetime.timedelta(seconds=int(seconds_elapsed)))
                    if self.percent_completed > 0:
                        seconds_remain = (seconds_elapsed * remaining) / completed
                        time_remain = '  Remaining: ' + str(datetime.timedelta(seconds=int(seconds_remain)))
                    else:
                        time_remain = ''
                    self.scanningpopup.scanning_text = "Importing "+format_size(total_size)+'  '+str(int(self.percent_completed))+'%  '+time_elapsed+time_remain
                    old_full_filename = os.path.join(photo[2], photo[0])
                    new_photo_fullpath = os.path.join(folder_name, photo[10])
                    new_full_filename = os.path.join(import_to, new_photo_fullpath)
                    thumbnail_data = app.Photo.thumbnail(photo[2], temporary=True)
                    if not app.Photo.exist(new_photo_fullpath):
                        photo[0] = new_photo_fullpath
                        photo[1] = folder_name
                        photo[2] = import_to
                        photo[6] = int(time.time())

                        try:
                            copy2(old_full_filename, new_full_filename)
                        except:
                            failed_files = failed_files + 1
                            imported_size = imported_size + photo[4]
                        else:
                            if self.delete_originals:
                                if os.path.isfile(new_full_filename):
                                    if os.path.getsize(new_full_filename) == os.path.getsize(old_full_filename):
                                        os.remove(old_full_filename)
                            app.Photo.add(photo)
                            # app.database_imported_add(photo[0], photo[10], photo[3])
                            if thumbnail_data:
                                thumbnail = thumbnail_data[2]
                                app.Photo.thumbnail_write(photo[0], int(time.time()), thumbnail, photo[13])
                            imported_size = imported_size+photo[4]
                            imported_files = imported_files + 1
                    else:
                        failed_files = failed_files + 1
                        imported_size = imported_size + photo[4]
                """
                imported_folders.append(folder_name)
        """


        raise ValueError('muste complete import')
        app.Photo.commit()
        app.Folder.commit()

        app.update_photoinfo(folders=imported_folders)
        self.scanningpopup.dismiss()
        if failed_files:
            failed = ' Could not import ' + str(failed_files) + ' files.'
        else:
            failed = ''
        if not self.cancel_scanning:
            if imported_files:
                app.message("Finished importing "+str(imported_files)+" files."+failed)
        else:
            if imported_files:
                app.message("Canceled importing, "+str(imported_files)+" files were imported."+failed)
            else:
                app.message("Canceled importing, no files were imported.")
        self.scanningpopup = None
        self.import_scanning = False
        Clock.schedule_once(lambda *dt: app.show_database())

    def set_delete_originals(self, state):
        """Enable the 'Delete Originals' option."""

        if state == 'down':
            self.delete_originals = True
        else:
            self.delete_originals = False

    def previous_album(self):
        """Switch to the previous album in the list."""

        database = self.ids['folders']
        selected_album = database.selected_node
        if selected_album:
            nodes = list(database.iterate_all_nodes())
            index = nodes.index(selected_album)
            if index <= 1:
                index = len(nodes)
            new_selected_album = nodes[index-1]
            database.select_node(new_selected_album)
            new_selected_album.on_press()
            database_container = self.ids['foldersContainer']
            database_container.scroll_to(new_selected_album)

    def next_album(self):
        """Switch to the next item on the list."""

        database = self.ids['folders']
        selected_album = database.selected_node
        if selected_album:
            nodes = list(database.iterate_all_nodes())
            index = nodes.index(selected_album)
            if index >= len(nodes)-1:
                index = 0
            new_selected_album = nodes[index+1]
            database.select_node(new_selected_album)
            new_selected_album.on_press()
            database_container = self.ids['foldersContainer']
            database_container.scroll_to(new_selected_album)

    def delete(self):
        """Remove selected files and place them in the unsorted folder."""

        if self.type == 'folder' or (self.type == 'extra' and self.selected == 'unsorted'):
            selected_files = self.get_selected_photos()
            for photo in selected_files:
                if self.selected != 'unsorted':
                    self.folders[self.selected]['photos'].remove(photo)
                    self.unsorted.append(photo)
            self.update_treeview()
            self.update_photolist()

    def add_folder(self):
        """Begin the add folder process, create an input popup."""

        content = InputPopup(hint='Folder Name', text='Enter A Folder Name:')
        app = App.get_running_app()
        content.bind(on_answer=self.add_folder_answer)
        self.popup = NormalPopup(title='Create Folder', content=content, size_hint=(None, None), size=(app.popup_x, app.button_scale * 4), auto_dismiss=False)
        self.popup.open()

    def add_folder_answer(self, instance, answer):
        """Confirm adding the folder.
        Arguments:
            instance: Dialog that called this function.
            answer: String, if set to 'yes', folder is created.
        """

        app = App.get_running_app()
        if answer == 'yes':
            text = instance.ids['input'].text.strip(' ')
            if text:
                if self.type == 'extra':
                    root = ''
                else:
                    root = self.selected
                path = os.path.join(root, text)
                if path not in self.folders:
                    self.folders[path] = {'name': text, 'parent': root, 'naming': False, 'title': '', 'description': '', 'year': 0, 'month': 0, 'day': 0, 'photos': []}
                else:
                    app.message("Folder already exists.")

        self.dismiss_popup()
        self.update_treeview()

    def delete_folder(self):
        """Delete the selected import folder and move photos to the unsorted folder."""

        if self.type == 'folder' and self.selected:
            folder_info = self.folders[self.selected]
            photos = folder_info['photos']
            for photo in photos:
                self.unsorted.append(photo)
            del self.folders[self.selected]
            self.selected = ''
            self.type = 'None'
            self.update_treeview()
            self.update_photolist()

    def toggle_select(self):
        """Toggles the selection of photos in the current album."""

        photos = self.ids['photos']
        photos.toggle_select()
        self.update_selected()

    def select_none(self):
        """Deselects all photos."""

        photos = self.ids['photos']
        photos.clear_selection()
        self.update_selected()

    def update_treeview(self):
        """Clears and repopulates the left-side folder list."""

        folder_list = self.ids['folders']

        #Clear the treeview list
        nodes = list(folder_list.iterate_all_nodes())
        for node in nodes:
            folder_list.remove_node(node)
        selected_node = None

        #folder_item = TreeViewButton(target='removed', type='extra', owner=self, view_album=False)
        #folder_item.folder_name = 'Removed (Never Scan Again)'
        #total_photos = len(self.removed)
        #folder_item.total_photos_numeric = total_photos
        #if total_photos > 0:
        #    folder_item.total_photos = '('+str(total_photos)+')'
        #folder_list.add_node(folder_item)
        #if self.selected == 'removed' and self.type == 'extra':
        #    selected_node = folder_item

        #Populate the 'Already Imported' folder
        folder_item = TreeViewButton(target='duplicates', type='extra', owner=self, view_album=False)
        folder_item.folder_name = 'Already Imported (Never Import Again)'
        total_photos = len(self.duplicates)
        folder_item.total_photos_numeric = total_photos
        if total_photos > 0:
            folder_item.total_photos = '('+str(total_photos)+')'
        folder_list.add_node(folder_item)
        if self.selected == 'duplicates' and self.type == 'extra':
            selected_node = folder_item

        #Populate the 'Unsorted' folder
        folder_item = TreeViewButton(target='unsorted', type='extra', owner=self, view_album=False)
        folder_item.folder_name = 'Unsorted (Not Imported This Time)'
        total_photos = len(self.unsorted)
        folder_item.total_photos_numeric = total_photos
        if total_photos > 0:
            folder_item.total_photos = '('+str(total_photos)+')'
        folder_list.add_node(folder_item)
        if self.selected == 'unsorted' and self.type == 'extra':
            selected_node = folder_item

        #Populate the importing folders
        sorted_folders = sorted(self.folders)
        self.total_size = 0
        to_parent = []
        added_nodes = {}
        for folder_date in sorted_folders:
            folder_info = self.folders[folder_date]
            target = folder_date
            folder_item = TreeViewButton(is_open=True, fullpath=target, dragable=True, target=target, type='folder', owner=self, view_album=False)
            if folder_info['naming']:
                folder_item.folder_name = naming(self.naming_method, title=folder_info['title'], year=folder_info['year'], month=folder_info['month'], day=folder_info['day'])
            else:
                folder_item.folder_name = folder_info['name']
            added_nodes[folder_date] = folder_item
            photos = folder_info['photos']
            for photo in photos:
                self.total_size = self.total_size + photo[4]
            total_photos = len(photos)
            folder_item.total_photos_numeric = total_photos
            if total_photos > 0:
                folder_item.total_photos = '('+str(total_photos)+')'
            if folder_info['parent']:
                to_parent.append([folder_item, folder_info['parent']])
            else:
                folder_list.add_node(folder_item)
            if self.selected == target and self.type == 'folder':
                selected_node = folder_item
        for item in to_parent:
            node = item[0]
            parent_name = item[1]
            if parent_name in added_nodes.keys():
                folder_list.add_node(node, parent=added_nodes[parent_name])
            else:
                folder_list.add_node(node)
        if selected_node:
            folder_list.select_node(selected_node)
        size_display = self.ids['totalSize']
        size_display.text = 'Total Size: '+format_size(self.total_size)

    def on_selected(self, instance, value):
        """Called when a photo is selected.  Activate the delete button, and update photo view."""

        delete_button = self.ids['deleteButton']
        delete_button.disabled = True
        self.update_photolist()

    def new_description(self, description_editor):
        """Called when the description field of the currently selected folder is edited.
        Update internal variables to match.
        Argument:
            description_editor: The input box that has been edited.
        """

        description = description_editor.text
        if self.type == 'folder':
            self.folders[self.selected]['description'] = description

    def new_title(self, title_editor):
        """Called when the title field of the currently selected folder is edited.
        Update internal variables to match.
        Argument:
            title_editor: The input box that has been edited.
        """

        title = title_editor.text
        if self.type == 'folder':
            self.folders[self.selected]['title'] = title
            folder_info = self.folders[self.selected]
            self.update_treeview()
            folder_name = self.ids['folderName']
            folder_name.text = naming(self.naming_method, title=folder_info['title'], year=folder_info['year'], month=folder_info['month'], day=folder_info['day'])

    def update_photolist(self):
        """Redraw the photo list view for the currently selected folder."""

        folder_name = self.ids['folderName']
        photos = []
        name = ''
        title_editor = self.ids['folderTitle']
        description_editor = self.ids['folderDescription']
        dragable = True

        #Viewing an input folder.
        if self.type == 'folder':
            if self.selected in self.folders:
                folder_info = self.folders[self.selected]
                title_editor.text = folder_info['title']
                title_editor.disabled = False
                description_editor.text = folder_info['description']
                description_editor.disabled = False
                photos = folder_info['photos']
                if folder_info['naming']:
                    name = naming(self.naming_method, title=folder_info['title'], year=folder_info['year'], month=folder_info['month'], day=folder_info['day'])
                else:
                    name = self.selected

        #Viewing a special sorting folder.
        else:
            title_editor.text = ''
            title_editor.disabled = True
            description_editor.text = ''
            description_editor.disabled = True
            if self.selected == 'unsorted':
                photos = self.unsorted
                name = 'Unsorted (Not Imported This Time)'
            elif self.selected == 'removed':
                photos = self.removed
                name = 'Removed (Never Scanned Again)'
            elif self.selected == 'duplicates':
                dragable = False
                photos = self.duplicates
                name = 'Already Imported (Never Import Again)'

        folder_name.text = name

        #Populate photo view
        photos_container = self.ids['photosContainer']
        datas = []
        for photo in photos:
            full_filename = os.path.join(photo.database_folder, photo.fullpath)
            fullpath = photo.fullpath
            database_folder = photo.database_folder
            video = os.path.splitext(full_filename)[1].lower() in movietypes
            data = {
                'fullpath': fullpath,
                'temporary': True,
                'photoinfo': photo.photoInfo(),
                'folder': self.selected,
                'database_folder': database_folder,
                'filename': full_filename,
                'target': self.selected,
                'type': self.type,
                'owner': self,
                'video': video,
                'photo_orientation': photo.orientation,
                'source': full_filename,
                'title': photo.owner,
                'selected': False,
                'selectable': True,
                'dragable': dragable
            }
            datas.append(data)
        photos_container.data = datas
        self.select_none()

    def find_photo(self, photo_path, photo_list):
        """Searches through a list of photoinfo objects to find the specified photo.
        Arguments:
            photo_path: The screenDatabase-relative path to the photo to search for.
            photo_list: The list of photo info objects to look through.
        Returns:
            False if nothing found
            Photo info list if match found.
        """

        for photo in photo_list:
            if photo[0] == photo_path:
                return photo
        return False

    def drop_widget(self, fullpath, position, dropped_type='file', aspect=1):
        """Called when a widget is dropped after being dragged.
        Determines what to do with the widget based on where it is dropped.
        Arguments:
            fullpath: String, file location of the object being dragged.
            position: List of X,Y window coordinates that the widget is dropped on.
            dropped_type: String, describes the object being dropped.  May be: 'folder' or 'file'
        """

        app = App.get_running_app()
        folder_list = self.ids['folders']
        folder_container = self.ids['foldersContainer']
        if folder_container.collide_point(position[0], position[1]):
            offset_x, offset_y = folder_list.to_widget(position[0], position[1])
            for widget in folder_list.children:
                if widget.collide_point(position[0], offset_y) and widget.type != 'None' and self.type != 'None' and not (widget.target == 'duplicates' and widget.type == 'extra'):

                    if dropped_type == 'folder':
                        #Dropped a folder
                        dropped_data = self.folders[fullpath]
                        new_path = os.path.join(widget.fullpath, dropped_data['name'])
                        if widget.fullpath != fullpath:
                            #this was actually a drag and not a long click
                            if new_path not in self.folders:
                                #this folder can be dropped here
                                old_parent = fullpath
                                dropped_data['parent'] = widget.fullpath
                                self.folders[new_path] = dropped_data
                                del self.folders[fullpath]

                                new_folders = {}
                                #rename child folders
                                for folder in self.folders:
                                    folder_info = self.folders[folder]
                                    parent = folder_info['parent']
                                    if old_parent and folder.startswith(old_parent):
                                        new_folder_path = new_path + folder[len(old_parent):]
                                        new_parent = new_path + parent[len(old_parent):]
                                        folder_info['parent'] = new_parent
                                        new_folders[new_folder_path] = folder_info
                                    else:
                                        new_folders[folder] = folder_info

                                self.folders = new_folders
                                self.update_treeview()
                                self.update_photolist()
                            else:
                                app.message("Invalid folder location.")
                    elif dropped_type == 'file':
                        #Dropped a file
                        photo_list = self.get_selected_photos(fullpath=True)
                        if fullpath not in photo_list:
                            photo_list.append(fullpath)
                        for photo_path in photo_list:
                            photo_info = False
                            if self.type == 'folder':
                                photo_info = self.find_photo(photo_path, self.folders[self.selected]['photos'])
                                if photo_info:
                                    self.folders[self.selected]['photos'].remove(photo_info)
                            else:
                                if self.selected == 'unsorted':
                                    photo_info = self.find_photo(photo_path, self.unsorted)
                                    if photo_info:
                                        self.unsorted.remove(photo_info)
                                elif self.selected == 'removed':
                                    photo_info = self.find_photo(photo_path, self.removed)
                                    if photo_info:
                                        self.removed.remove(photo_info)
                            if photo_info:
                                if widget.type == 'folder':
                                    self.folders[widget.target]['photos'].append(photo_info)
                                else:
                                    if widget.target == 'unsorted':
                                        self.unsorted.append(photo_info)
                                    elif widget.target == 'removed':
                                        self.removed.append(photo_info)

                        self.type = widget.type
                        self.selected = widget.target
                        self.update_treeview()
                        self.select_none()
                    break

    def update_selected(self):
        """Updates the delete button when files are selected or unselected.  Disables button if nothing is selected."""

        if self.type == 'folder' or (self.type == 'extra' and self.selected == 'unsorted'):
            photos = self.ids['photos']
            if photos.selected_nodes:
                selected = True
            else:
                selected = False
            delete_button = self.ids['deleteButton']
            if self.type != 'extra' and self.selected != 'unsorted':
                delete_button.disabled = not selected

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

    def text_input_active(self):
        """Detects if any text input fields are currently active (being typed in).
        Returns: True or False
        """

        input_active = False
        for widget in self.walk(restrict=True):
            if widget.__class__.__name__ == 'NormalInput' or widget.__class__.__name__ == 'FloatInput' or widget.__class__.__name__ == 'IntegerInput':
                if widget.focus:
                    input_active = True
                    break
        return input_active

    def key(self, key):
        """Handles keyboard shortcuts, performs the actions needed.
        Argument:
            key: The name of the key command to perform.
        """

        if self.text_input_active():
            pass
        else:
            if not self.popup or (not self.popup.open):
                if key == 'left' or key == 'up':
                    self.previous_album()
                if key == 'right' or key == 'down':
                    self.next_album()
                if key == 'delete':
                    self.delete()
                if key == 'a':
                    self.toggle_select()
            elif self.popup and self.popup.open:
                if key == 'enter':
                    self.popup.content.dispatch('on_answer', 'yes')