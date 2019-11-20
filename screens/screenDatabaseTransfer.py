import os
from shutil import move
import threading
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty, NumericProperty

from generalcommands import to_bool, local_path, verify_copy
from generalElements.buttons.MenuButton import MenuButton
from generalElements.dropDowns.NormalDropDown import NormalDropDown
from generalElements.popups.ScanningPopup import ScanningPopup
from generalElements.popups.MoveConfirmPopup import MoveConfirmPopup
from generalElements.popups.ConfirmPopup import ConfirmPopup
from generalconstants import *
from screenDatabaseUtil.databaseSortDropDown import DatabaseSortDropDown

from kivy.lang.builder import Builder
Builder.load_string("""
<ScreenDatabaseTransfer>:
    canvas.before:
        Color:
            rgba: app.theme.background
        Rectangle:
            pos: self.pos
            size: self.size
    id: transferScreen
    BoxLayout:
        orientation: 'vertical'
        MainHeader:
            NormalButton:
                text: 'Back To Library'
                on_release: app.show_database()
            NormalToggle:
                text: '  Quick Move  ' if self.state == 'normal' else '  Verify Move  '
                state: 'down' if app.config.get("Settings", "quicktransfer") == '0' else 'normal'
                on_release: app.toggle_quicktransfer(self)
            HeaderLabel:
                text: 'Database Folder Transfer'
            InfoLabel:
            DatabaseLabel:
            SettingsButton:
        BoxLayout:
            orientation: 'horizontal'
            BoxLayout:
                orientation: 'vertical'
                id: leftArea
                Header:
                    MenuStarterButtonWide:
                        size_hint_x: 1
                        id: leftDatabaseMenu
                        text: root.left_database
                        on_release: root.database_dropdown_left.open(self)
                    MediumBufferX:
                    ShortLabel:
                        text: 'Sort:'
                    MenuStarterButton:
                        size_hint_x: 1
                        text: root.left_sort_method
                        on_release: root.left_sort_dropdown.open(self)
                    ReverseToggle:
                        state: 'down' if root.left_sort_reverse else 'normal'
                        on_press: root.left_resort_reverse(self.state)
                    NormalButton:
                        text: '  Toggle Select  '
                        width: self.texture_size[0]
                        on_release: leftDatabaseArea.toggle_select()
                MainArea:
                    PhotoListRecycleView:
                        id: leftDatabaseHolder
                        viewclass: 'RecycleTreeViewButton'
                        scroll_distance: 10
                        scroll_timeout: 200
                        bar_width: int(app.button_scale * .5)
                        bar_color: app.theme.scroller_selected
                        bar_inactive_color: app.theme.scroller
                        scroll_type: ['bars', 'content']
                        SelectableRecycleBoxLayout:
                            multiselect: True
                            id: leftDatabaseArea
            MediumBufferX:
            BoxLayout:
                orientation: 'vertical'
                id: rightArea
                Header:
                    MenuStarterButtonWide:
                        size_hint_x: 1
                        id: rightDatabaseMenu
                        text: root.right_database
                        on_release: root.database_dropdown_right.open(self)
                    MediumBufferX:
                    ShortLabel:
                        text: 'Sort:'
                    MenuStarterButton:
                        size_hint_x: 1
                        text: root.right_sort_method
                        on_release: root.right_sort_dropdown.open(self)
                    ReverseToggle:
                        state: 'down' if root.right_sort_reverse else 'normal'
                        on_press: root.right_resort_reverse(self.state)
                    NormalButton:
                        text: '  Toggle Select  '
                        width: self.texture_size[0]
                        on_release: rightDatabaseArea.toggle_select()
                MainArea:
                    PhotoListRecycleView:
                        id: rightDatabaseHolder
                        viewclass: 'RecycleTreeViewButton'
                        scroll_distance: 10
                        scroll_timeout: 200
                        bar_width: int(app.button_scale * .5)
                        bar_color: app.theme.scroller_selected
                        bar_inactive_color: app.theme.scroller
                        scroll_type: ['bars', 'content']
                        SelectableRecycleBoxLayout:
                            multiselect: True
                            id: rightDatabaseArea


""")

class ScreenDatabaseTransfer(Screen):
    """Database folder transfer screen layout."""

    popup = None
    database_dropdown_left = ObjectProperty()
    database_dropdown_right = ObjectProperty()
    left_database = StringProperty()
    right_database = StringProperty()
    left_sort_method = StringProperty()
    right_sort_method = StringProperty()
    left_sort_reverse = BooleanProperty()
    right_sort_reverse = BooleanProperty()
    left_sort_dropdown = ObjectProperty()
    right_sort_dropdown = ObjectProperty()
    quick = BooleanProperty(False)

    transfer_from = StringProperty()
    transfer_to = StringProperty()
    folders = ListProperty()

    cancel_copying = BooleanProperty(False)
    copying = BooleanProperty(False)
    copyingpopup = ObjectProperty()
    percent_completed = NumericProperty(0)
    copyingthread = ObjectProperty()

    selected = ''
    expanded_folders = []

    def has_popup(self):
        """Detects if the current screen has a popup active.
        Returns: True or False
        """

        if self.popup:
            if self.popup.open:
                return True
        return False

    def dismiss_extra(self):
        """Cancels the copy process if it is running"""

        if self.copying:
            self.cancel_copy()
            return True
        else:
            return False

    def dismiss_popup(self, *_):
        """Close a currently open popup for this screen."""

        if self.popup:
            self.popup.dismiss()
            self.popup = None

    def key(self, key):
        """Dummy function, not valid for this screen but the app calls it."""

        if not self.popup or (not self.popup.open):
            del key

    def resort_method_left(self, method):
        self.left_sort_method = method
        self.refresh_left_database()

    def resort_method_right(self, method):
        self.right_sort_method = method
        self.refresh_right_database()

    def left_resort_reverse(self, reverse):
        sort_reverse = True if reverse == 'down' else False
        self.left_sort_reverse = sort_reverse
        self.refresh_left_database()

    def right_resort_reverse(self, reverse):
        sort_reverse = True if reverse == 'down' else False
        self.right_sort_reverse = sort_reverse
        self.refresh_right_database()

    def on_enter(self):
        """Called when screen is entered, set up the needed variables and image viewer."""

        app = App.get_running_app()

        #set up sort buttons
        self.left_sort_dropdown = DatabaseSortDropDown()
        self.left_sort_dropdown.bind(on_select=lambda instance, x: self.resort_method_left(x))
        self.left_sort_method = app.config.get('Sorting', 'database_sort')
        self.left_sort_reverse = to_bool(app.config.get('Sorting', 'database_sort_reverse'))
        self.right_sort_dropdown = DatabaseSortDropDown()
        self.right_sort_dropdown.bind(on_select=lambda instance, x: self.resort_method_right(x))
        self.right_sort_method = app.config.get('Sorting', 'database_sort')
        self.right_sort_reverse = to_bool(app.config.get('Sorting', 'database_sort_reverse'))

        databases = app.get_database_directories()
        self.database_dropdown_left = NormalDropDown()
        self.database_dropdown_right = NormalDropDown()
        for database in databases:
            database_button_left = MenuButton(text=database)
            database_button_left.bind(on_release=self.set_database_left)
            self.database_dropdown_left.add_widget(database_button_left)
            database_button_right = MenuButton(text=database)
            database_button_right.bind(on_release=self.set_database_right)
            self.database_dropdown_right.add_widget(database_button_right)
        self.left_database = databases[0]
        self.right_database = databases[1]
        self.update_treeview()

    def set_database_left(self, button):
        self.database_dropdown_left.dismiss()
        if self.right_database == button.text:
            self.right_database = self.left_database
            self.refresh_right_database()
        self.left_database = button.text
        self.refresh_left_database()

    def set_database_right(self, button):
        self.database_dropdown_right.dismiss()
        if self.left_database == button.text:
            self.left_database = self.right_database
            self.refresh_left_database()
        self.right_database = button.text
        self.refresh_right_database()

    def refresh_left_database(self):
        database_area = self.ids['leftDatabaseHolder']
        self.refresh_database_area(database_area, self.left_database, self.left_sort_method, self.left_sort_reverse)

    def refresh_right_database(self):
        database_area = self.ids['rightDatabaseHolder']
        self.refresh_database_area(database_area, self.right_database, self.right_sort_method, self.right_sort_reverse)

    def drop_widget(self, fullpath, position, dropped_type, aspect=1):
        """Called when a widget is dropped after being dragged.
        Determines what to do with the widget based on where it is dropped.
        Arguments:
            fullpath: String, file location of the object being dragged.
            position: List of X,Y window coordinates that the widget is dropped on.
            dropped_type: String, describes the object's screenDatabase origin directory
        """

        app = App.get_running_app()
        transfer_from = dropped_type
        left_database_holder = self.ids['leftDatabaseHolder']
        left_database_area = self.ids['leftDatabaseArea']
        right_database_holder = self.ids['rightDatabaseHolder']
        right_database_area = self.ids['rightDatabaseArea']
        transfer_to = None
        folders = []
        if left_database_holder.collide_point(position[0], position[1]):
            if transfer_from != self.left_database:
                selects = right_database_area.selects
                for select in selects:
                    folders.append(local_path(select['fullpath']))
                transfer_to = self.left_database
        elif right_database_holder.collide_point(position[0], position[1]):
            if transfer_from != self.right_database:
                selects = left_database_area.selects
                for select in selects:
                    folders.append(local_path(select['fullpath']))
                transfer_to = self.right_database
        if transfer_to:
            if fullpath not in folders:
                folders.append(fullpath)
            #remove subfolders
            removes = []
            for folder in folders:
                for fold in folders:
                    if folder.startswith(fold+os.path.sep):
                        removes.append(folder)
                        break
            reduced_folders = []
            for folder in folders:
                if folder not in removes:
                    reduced_folders.append(folder)

            content = ConfirmPopup(text='Move These Folders From "'+transfer_from+'" to "'+transfer_to+'"?', yes_text='Move', no_text="Don't Move", warn_yes=True)
            content.bind(on_answer=self.move_folders)
            self.transfer_to = transfer_to
            self.transfer_from = transfer_from
            self.folders = reduced_folders
            self.popup = MoveConfirmPopup(title='Confirm Move', content=content, size_hint=(None, None), size=(app.popup_x, app.button_scale * 4), auto_dismiss=False)
            self.popup.open()

    def cancel_copy(self, *_):
        self.cancel_copying = True

    def move_folders(self, instance, answer):
        del instance
        app = App.get_running_app()
        self.dismiss_popup()
        if answer == 'yes':
            self.cancel_copying = False
            self.copyingpopup = ScanningPopup(title='Moving Files', auto_dismiss=False, size_hint=(None, None), size=(app.popup_x, app.button_scale * 4))
            self.copyingpopup.open()
            scanning_button = self.copyingpopup.ids['scanningButton']
            scanning_button.bind(on_release=self.cancel_copy)

            # Start importing thread
            self.percent_completed = 0
            self.copyingthread = threading.Thread(target=self.move_process)
            self.copyingthread.start()

    def move_process(self):
        app = App.get_running_app()
        self.quick = app.config.get("Settings", "quicktransfer")
        transfer_from = self.transfer_from
        transfer_to = self.transfer_to
        folders = self.folders

        total_files = 0
        total_size = 0
        for folder in folders:
            origin = os.path.join(transfer_from, folder)
            for root, dirs, files in os.walk(origin):
                for file in files:
                    total_files = total_files + 1
                    total_size = total_size + os.path.getsize(os.path.join(root, file))

        current_files = 0
        current_size = 0
        for folder in folders:
            origin = os.path.join(transfer_from, folder)
            #target = os.path.join(transfer_to, folder)
            for root, dirs, files in os.walk(origin, topdown=False):
                for file in files:
                    copy_from = os.path.join(root, file)
                    fullpath = os.path.relpath(copy_from, transfer_from)
                    copy_to = os.path.join(transfer_to, fullpath)
                    directory = os.path.split(copy_to)[0]
                    if not os.path.isdir(directory):
                        os.makedirs(directory)
                    self.copyingpopup.scanning_text = "Moving "+str(current_files)+" of "+str(total_files)+"."
                    self.copyingpopup.scanning_percentage = (current_size / total_size) * 100

                    if self.cancel_copying:
                        app.message("Canceled Moving Files, "+str(current_files)+" Files Moved.")
                        app.photos.commit()
                        self.copyingpopup.dismiss()
                        return
                    fileinfo = app.Photo.exist(fullpath)
                    copied = False
                    if self.quick == '1':
                        try:
                            move(copy_from, copy_to)
                            copied = True
                        except:
                            pass
                    else:
                        result = verify_copy(copy_from, copy_to)
                        if result is True:
                            os.remove(copy_from)
                            copied = True
                    if copied:
                        if fileinfo:
                            fileinfo[2] = transfer_to
                            app.Photo.moved(fileinfo)
                        current_files = current_files + 1
                        current_size = current_size + os.path.getsize(copy_to)
                    if os.path.isfile(copy_from):
                        if os.path.split(copy_from)[1] == '.photoinfo.ini':
                            os.remove(copy_from)
                try:
                    os.rmdir(root)
                except:
                    pass
        self.copyingpopup.dismiss()
        app.photos.commit()
        app.message("Finished Moving "+str(current_files)+" Files.")
        Clock.schedule_once(self.update_treeview)

    def toggle_expanded_folder(self, folder):
        if folder in self.expanded_folders:
            self.expanded_folders.remove(folder)
        else:
            self.expanded_folders.append(folder)
        self.update_treeview()

    def refresh_database_area(self, database, database_folder, sort_method, sort_reverse):
        app = App.get_running_app()

        database.data = []
        data = []

        #Get and sort folder list
        unsorted_folders = app.Photo.by_folder(database_folder=database_folder)
        if sort_method in ['Amount', 'Title', 'Imported', 'Modified']:
            folders = []
            for folder in unsorted_folders:
                sortby = 0
                folderpath = folder
                if sort_method == 'Amount':
                    sortby = len(app.Photo.by_folder(folderpath, database=database_folder))
                elif sort_method == 'Title':
                    folderinfo = app.Folder.exist(folderpath)
                    if folderinfo:
                        sortby = folderinfo[1]
                    else:
                        sortby = folderpath
                elif sort_method == 'Imported':
                    folder_photos = app.Photo.by_folder(folderpath, database=database_folder)
                    for folder_photo in folder_photos:
                        if folder_photo[6] > sortby:
                            sortby = folder_photo[6]
                elif sort_method == 'Modified':
                    folder_photos = app.Photo.by_folder(folderpath, database=database_folder)
                    for folder_photo in folder_photos:
                        if folder_photo[7] > sortby:
                            sortby = folder_photo[7]

                folders.append([sortby, folderpath])
            sorted_folders = sorted(folders, key=lambda x: x[0], reverse=sort_reverse)
            sorts, all_folders = zip(*sorted_folders)
        else:
            all_folders = sorted(unsorted_folders, reverse=sort_reverse)

        #Parse and sort folders and subfolders
        root_folders = []
        for full_folder in all_folders:
            if full_folder and not any(avoidfolder in full_folder for avoidfolder in avoidfolders):
                newname = full_folder
                children = root_folders
                parent_folder = ''
                while os.path.sep in newname:
                    #split the base path and the leaf paths
                    root, leaf = newname.split(os.path.sep, 1)
                    parent_folder = os.path.join(parent_folder, root)

                    #check if the root path is already in the tree
                    root_element = False
                    for child in children:
                        if child['folder'] == root:
                            root_element = child
                    if not root_element:
                        children.append({'folder': root, 'full_folder': parent_folder, 'children': []})
                        root_element = children[-1]
                    children = root_element['children']
                    newname = leaf
                root_element = False
                for child in children:
                    if child['folder'] == newname:
                        root_element = child
                if not root_element:
                    children.append({'folder': newname, 'full_folder': full_folder, 'children': []})

        folder_data = self.populate_folders(root_folders, self.expanded_folders, sort_method, sort_reverse, database_folder)
        data = data + folder_data

        database.data = data

    def populate_folders(self, folder_root, expanded, sort_method, sort_reverse, database_folder):
        app = App.get_running_app()
        folders = []
        folder_root = self.sort_folders(folder_root, sort_method, sort_reverse)
        for folder in folder_root:
            full_folder = folder['full_folder']
            expandable = True if len(folder['children']) > 0 else False
            is_expanded = True if full_folder in expanded else False
            folder_info = app.Folder.exist(full_folder)
            if folder_info:
                subtext = folder_info[1]
            else:
                subtext = ''
            folder_element = {
                'fullpath': full_folder,
                'folder_name': folder['folder'],
                'target': full_folder,
                'type': 'Folder',
                'total_photos': '',
                'total_photos_numeric': 0,
                'displayable': True,
                'expandable': expandable,
                'expanded': is_expanded,
                'owner': self,
                'indent': 1 + full_folder.count(os.path.sep),
                'subtext': subtext,
                'height': app.button_scale * (1.5 if subtext else 1),
                'end': False,
                'droptype': database_folder,
                'dragable': True
            }
            folders.append(folder_element)
            if is_expanded:
                if len(folder['children']) > 0:
                    more_folders = self.populate_folders(folder['children'], expanded, sort_method, sort_reverse, database_folder)
                    folders = folders + more_folders
                    folders[-1]['end'] = True
                    folders[-1]['height'] = folders[-1]['height'] + int(app.button_scale * 0.1)
        return folders

    def sort_folders(self, sort_folders, sort_method, sort_reverse):
        if sort_method in ['Amount', 'Title', 'Imported', 'Modified']:
            app = App.get_running_app()
            folders = []
            for folder in sort_folders:
                sortby = 0
                folderpath = folder['full_folder']
                if sort_method == 'Amount':
                    sortby = len(app.Photo.by_folder(folderpath))
                elif sort_method == 'Title':
                    folderinfo = app.Folder.exist(folderpath)
                    if folderinfo:
                        sortby = folderinfo[1]
                    else:
                        sortby = folderpath
                elif sort_method == 'Imported':
                    folder_photos = app.Photo.by_folder(folderpath)
                    for folder_photo in folder_photos:
                        if folder_photo[6] > sortby:
                            sortby = folder_photo[6]
                elif sort_method == 'Modified':
                    folder_photos = app.Photo.by_folder(folderpath)
                    for folder_photo in folder_photos:
                        if folder_photo[7] > sortby:
                            sortby = folder_photo[7]

                folders.append([sortby, folder])
            sorted_folders = sorted(folders, key=lambda x: x[0], reverse=sort_reverse)
            sorts, all_folders = zip(*sorted_folders)
        else:
            all_folders = sorted(sort_folders, key=lambda x: x['folder'], reverse=sort_reverse)

        return all_folders

    def update_treeview(self, *_):
        self.refresh_left_database()
        self.refresh_right_database()

