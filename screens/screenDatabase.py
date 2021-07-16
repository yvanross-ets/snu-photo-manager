from kivy.clock import Clock
from kivy.cache import Cache
from kivy.animation import Animation
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from functools import partial


from TreeViewItemModels.Favorites import Favorites
from TreeViewItemModels.Tags import Tags
from TreeViewItemModels.Folders import Folders
from TreeViewItemModels.Faces import Faces
from TreeViewItem.TreeViewItemFaces import TreeViewItemFaces
from TreeViewItemModels.Persons import Persons

from TreeViewItem.TreeViewItemFolders import TreeViewItemFolders
from TreeViewItem.TreeViewItemFolder import TreeViewItemFolder
from TreeViewItem.TreeViewItemTags import TreeViewItemTags
from TreeViewItem.TreeViewItemPersons import TreeViewItemPersons
from TreeViewItem.TreeViewItemFavorites import TreeViewItemFavorites
from TreeViewItem.TreeViewItemCountries import TreeViewItemCountries
from TreeViewItem.TreeViewItemDaysOfPhotosWithoutPlace import TreeViewItemDaysOfPhotosWithoutPlace

from generalcommands import to_bool
from generalElements.dropDowns.NormalDropDown import NormalDropDown
from generalElements.popups.InputPopup import InputPopup
from generalElements.popups.NormalPopup import NormalPopup
from generalElements.popups.ConfirmPopup import ConfirmPopup
from generalconstants import *
from screenDatabaseUtil.databaseSortDropDown import DatabaseSortDropDown
from screenDatabaseUtil.folderDetails import FolderDetails
from screenDatabaseUtil.albumDetails import AlbumDetails
from models.PhotosTags import *
from TreeViewItemModels.Countries import Countries
from TreeViewItemModels.DaysOfPhotosWithoutPlace import DaysOfPhotosWithoutPlace

# import kivy requested widget
from generalElements.labels.InfoLabel import InfoLabel
from generalElements.splitters.SplitterPanelLeft import SplitterPanelLeft
from generalElements.buttons.ToogleBase import ToggleBase
from generalElements.photos.PhotoListRecycleView import PhotoListRecycleView
from generalElements.selectables.SelectableRecycleBoxLayout import SelectableRecycleBoxLayout
from generalElements.inputs.NormalInput import NormalInput
from generalElements.views.NormalRecycleView import NormalRecycleView
from generalElements.selectables.SelectableRecycleGrid import SelectableRecycleGrid
from generalElements.photos.PhotoRecycleThumb import PhotoRecycleThumb
from generalElements.treeviews.RecycleTreeViewButton import RecycleTreeViewButton
from generalElements.images.AsyncThumbnail import AsyncThumbnail




from kivy.lang.builder import Builder
Builder.load_string("""


<ScreenDatabase>:
    canvas.before:
        Color:
            rgba: app.theme.background
        Rectangle:
            pos: self.pos
            size: self.size
    id: screenDatabase
    BoxLayout:
        focus: True
        orientation: 'vertical'
        MainHeader:
            NormalButton:
                text: '  Import  '
                on_release: app.show_import()
                disabled: app.database_scanning
            NormalButton:
                size_hint_x: None
                width: self.texture_size[0] + 20 if not app.database_scanning else 0
                opacity: 0 if app.database_scanning else 1
                text: '  Update Database  '
                on_release: app.database_rescan()
                disabled: app.database_scanning
            NormalButton:
                size_hint_x: None
                width: self.texture_size[0] + 20 if app.database_scanning else 0
                opacity: 1 if app.database_scanning else 0
                text: '  Cancel Database Scan  '
                on_release: app.cancel_database_import()
                disabled: not app.database_scanning
                warn: True
            NormalButton:
                size_hint_x: None
                width: self.texture_size[0] + 20
                text: '  Database Transfer  '
                on_release: app.show_transfer()
                disabled: app.single_database or app.database_scanning
            HeaderLabel:
                text: 'Photo Database'
            InfoLabel:
            DatabaseLabel:
            SettingsButton:
        BoxLayout:
            orientation: 'horizontal'
            SplitterPanelLeft:
                id: leftpanel
                #width: app.leftpanel_width
                BoxLayout:
                    orientation: 'vertical'
                    Header:
                        size_hint_y: None
                        height: app.button_scale
                        ShortLabel:
                            text: 'Sort:'
                        MenuStarterButtonWide:
                            id: sortButton
                            text: root.sort_method
                            on_release: root.sort_dropdown.open(self)
                        ReverseToggle:
                            id: sortReverseButton
                            state: root.sort_reverse_button
                            on_press: root.resort_reverse(self.state)
                    PhotoListRecycleView:
                        id: screenDatabase
                        viewclass: 'RecycleTreeViewButton'
                        scroll_distance: 10
                        scroll_timeout: 200
                        bar_width: int(app.button_scale * .5)
                        bar_color: app.theme.scroller_selected
                        bar_inactive_color: app.theme.scroller
                        scroll_type: ['bars', 'content']
                        SelectableRecycleBoxLayout:
                            id: databaseInterior
                    DatabaseOptions:
                        id: databaseOptionsArea
                        orientation: 'vertical'
                        height: app.button_scale * (1 + (5*self.height_scale)) if app.simple_interface else app.button_scale * 2
                        size_hint_y: None
                        BoxLayout:
                            canvas.before:
                                Color:
                                    rgba: app.theme.menu_background if app.simple_interface else app.theme.header_background
                                Rectangle:
                                    size: self.size
                                    pos: self.pos
                                    source: 'data/buttonflat.png' if app.simple_interface else 'data/headerbg.png'
                            orientation: 'vertical'
                            size_hint_y: 1
                            opacity: databaseOptionsArea.height_scale if app.simple_interface else 1
                            disabled: False if (databaseOptions.state == 'down' or not app.simple_interface) else True
                            BoxLayout:
                                orientation: 'vertical' if app.simple_interface else 'horizontal'
                                NormalLabel:
                                    size_hint_y: 1
                                    id: operationType
                                    text: ''
                                NormalButton:
                                    size_hint_y: 1
                                    id: newFolder
                                    size_hint_x: 1
                                    text: 'New'
                                    on_release: root.new_item()
                                    disabled: not root.can_new_folder or app.database_scanning
                                NormalButton:
                                    size_hint_y: 1
                                    id: renameFolder
                                    size_hint_x: 1
                                    text: 'Rename'
                                    on_release: root.rename_item()
                                    disabled: not root.can_rename_folder or app.database_scanning
                                NormalButton:
                                    size_hint_y: 1
                                    id: deleteFolder
                                    size_hint_x: 1
                                    text: 'Delete'
                                    warn: True
                                    on_release: root.delete_item()
                                    disabled: not root.can_delete_folder or app.database_scanning
                            BoxLayout:
                                size_hint_y: None
                                height: app.button_scale
                                NormalInput:
                                    size_hint_y: 1
                                    multiline: False
                                    hint_text: 'Search...'
                                    text: root.search_text
                                    on_text: root.search(self.text)
                                NormalButton:
                                    size_hint_y: 1
                                    text: 'Clear'
                                    on_release: root.clear_search()
                        NormalToggle:
                            id: databaseOptions
                            size_hint_x: 1
                            text: 'Database Options'
                            height: app.button_scale if app.simple_interface else 0
                            opacity: 1 if app.simple_interface else 0
                            disabled: False if app.simple_interface else True
                            on_press: databaseOptionsArea.set_hidden(self.state)
            BoxLayout:
                orientation: 'vertical'
                Header:
                    ShortLabel:
                        id: folderType
                        text: ''
                    NormalLabel:
                        id: folderPath
                        text: ''
                    LargeBufferX:
                    ShortLabel:
                        text: 'Sort:'
                    MenuStarterButton:
                        size_hint_x: None
                        width: self.texture_size[0] + 80
                        id: albumSortButton
                        text: root.album_sort_method
                        on_release: root.album_sort_dropdown.open(self)
                    ReverseToggle:
                        id: albumSortReverseButton
                        state: root.album_sort_reverse_button
                        on_press: root.album_resort_reverse(self.state)
                GridLayout:
                    id: folderDetails
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    disabled: app.database_scanning
                MainArea:
                    NormalRecycleView:
                        data: root.data
                        id: photosContainer
                        viewclass: 'PhotoRecycleThumb'
                        SelectableRecycleGrid:
                            scale: root.scale
                            id: photos
                Header:
                    HalfSlider:
                        min: root.scale_min
                        max: root.scale_max
                        value: root.scale
                        on_value: root.scale = self.value
                    #Label:
                    #    text: ''
                    NormalButton:
                        text: 'Browse Folder'
                        disabled: not root.can_browse
                        opacity: 1 if root.can_browse else 0
                        width: (self.texture_size[0] + app.button_scale) if root.can_browse else 0
                        on_release: root.open_browser()
                    NormalButton:
                        text: 'Create Collage'
                        on_release: app.show_collage()
                        disabled: not root.can_export
                    NormalButton:
                        text: 'Export'
                        disabled: not root.can_export
                        on_release: root.export()
                    NormalButton:
                        text: 'Toggle Select'
                        on_release: root.toggle_select()
                    NormalButton:
                        id: deleteButton
                        text: 'Delete Selected'
                        disabled: not root.photos_selected or app.database_scanning
                        on_release: root.delete_selected_confirm()
                        warn: True
                    MenuStarterButton:
                        width: 0 if app.simple_interface else self.texture_size[0] + app.button_scale
                        opacity: 0 if app.simple_interface else 1
                        size_hint_x: 0 if app.simple_interface else 1
                        id: albumButton
                        text: 'Add To Person...'
                        disabled: not root.photos_selected or app.database_scanning
                        on_release: root.person_menu.open(self)
                    MenuStarterButton:
                        width: 0 if app.simple_interface else self.texture_size[0] + app.button_scale
                        opacity: 0 if app.simple_interface else 1
                        size_hint_x: 0 if app.simple_interface else 1
                        id: albumButton
                        text: 'Add To Location...'
                        disabled: not root.photos_selected or app.database_scanning
                        on_release: root.album_menu.open(self)
                    MenuStarterButton:
                        width: 0 if app.simple_interface else self.texture_size[0] + app.button_scale
                        opacity: 0 if app.simple_interface else 1
                        size_hint_x: 0 if app.simple_interface else 1
                        id: albumButton
                        text: 'Add To Album...'
                        disabled: not root.photos_selected or app.database_scanning
                        on_release: root.album_menu.open(self)
                    MenuStarterButton:
                        width: 0 if app.simple_interface else self.texture_size[0] + app.button_scale
                        opacity: 0 if app.simple_interface else 1
                        size_hint_x: 0 if app.simple_interface else 1
                        id: tagButton
                        text: 'Add Tag To...'
                        disabled: not root.photos_selected or app.database_scanning
                        on_release: root.tag_menu.open(self)




""")


class ScreenDatabase(Screen):
    """Screen layout for the main photo screenDatabase."""
    selected_item = ObjectProperty()
    type = StringProperty('folder')  #Currently selected type: folder, album, tag
    selected = ObjectProperty('') #Currently selected album in the screenDatabase, may be blank
    displayable = BooleanProperty(False)
    sort_dropdown = ObjectProperty()  #Database sorting menu
    sort_method = StringProperty('Name')  #Currently selected screenDatabase sort mode
    sort_reverse = BooleanProperty(False)  #Database sorting reversed or not
    album_sort_dropdown = ObjectProperty()  #Album sorting menu
    album_sort_method = StringProperty('Name')  #Currently selected album sort mode
    album_sort_reverse = BooleanProperty(False)  #Album sorting reversed or not
    folder_details = ObjectProperty()  #Holder for the folder details widget
    album_details = ObjectProperty()  #Holder for the album details widget
    popup = None  #Holder for the popup dialog widget
    photos = []  #List of photo infos in the currently displayed album
    can_export = BooleanProperty(False)  #Controls if the export button in the album view area is enabled
    sort_reverse_button = StringProperty('normal')
    album_sort_reverse_button = StringProperty('normal')
    tag_menu = ObjectProperty()
    album_menu = ObjectProperty()
    person_menu = ObjectProperty()
    data = ListProperty()
    expanded_albums = BooleanProperty(True)
    expanded_tags = BooleanProperty(True)
    expanded_persons = BooleanProperty(True)
    expanded_folders = BooleanProperty(True)
    expanded_countries = BooleanProperty(True)

    folders = []
    update_folders = True
    search_text = StringProperty()
    search_refresh = ObjectProperty()
    photos_selected = BooleanProperty(False)
    can_delete_folder = BooleanProperty(False)
    can_rename_folder = BooleanProperty(False)
    can_new_folder = BooleanProperty(False)
    can_browse = BooleanProperty(False)
    scale = NumericProperty(1)  #Controls the scale of picture widgets
    scale_min = .5
    scale_max = 3

    def open_browser(self):
        if self.can_browse:
            try:
                import webbrowser
                folders = []
                for photo in self.photos:
                    path = os.path.join(photo[Photo.DATABASEFOLDER], photo[Photo.FULLPATH])
                    folders.append(path)
                if folders:
                    folder = max(set(folders), key=folders.count)
                    webbrowser.open(folder)
            except:
                pass

    def update_can_browse(self):
        if platform in ['win', 'linux', 'macosx'] and self.type.lower() == 'folder' and self.displayable:
            self.can_browse = True
        else:
            self.can_browse = False

    def clear_search(self, *_):
        self.search_text = ''

    def search(self, text):
        self.search_text = text
        if self.tag_menu:
            Clock.unschedule(self.search_refresh)
            self.search_refresh = Clock.schedule_once(self.create_treeview, 0.5)

    #   add_item
    def new_item(self, *_):
        photoListRecyclerView = self.ids['screenDatabase']
        self.selected_item.new_item(photoListRecyclerView)
        # if self.type == 'Album':
        #     self.new_album()
        #
        # elif self.type == 'Tag':
        #     self.new_tag()
        #
        # elif self.type == 'Person':
        #     self.new_person()
        #
        # else:
        #     pass



    def rename_item(self, *_):
        photoListRecyclerView = self.ids['screenDatabase']
        self.selected_item.rename_item(photoListRecyclerView)

        # if self.type == 'Album':
        #     pass
        #
        # elif self.type == 'Tag':
        #     pass
        # elif self.type == 'Person':
        #     pass
        #
        # else:
        #     pass



    def delete_item(self, *_):
        photoListRecyclerView = self.ids['screenDatabase']
        self.selected_item.delete_item(photoListRecyclerView)




    def get_selected_photos(self):
        photos = self.ids['photos']
        selected_indexes = photos.selected_nodes
        photos_container = self.ids['photosContainer']
        selected_photos = []
        for selected in selected_indexes:
                selected_photos.append(photos_container.data[selected]['photo'])
        return selected_photos

    def on_sort_reverse(self, *_):
        """Updates the sort reverse button's state variable, since kivy doesnt just use True/False for button states."""

        app = App.get_running_app()
        self.sort_reverse_button = 'down' if to_bool(app.config.get('Sorting', 'database_sort_reverse')) else 'normal'

    def on_album_sort_reverse(self, *_):
        """Updates the sort reverse button's state variable, since kivy doesnt just use True/False for button states."""

        app = App.get_running_app()
        sort_reverse = to_bool(app.config.get('Sorting', 'album_sort_reverse'))
        self.album_sort_reverse_button = 'down' if sort_reverse else 'normal'

    def export(self):
        """Switches the app to export mode with the current selected album."""

        if self.selected and self.type != 'None':
            app = App.get_running_app()
            app.export_target = self.selected
            app.export_type = self.type
            app.show_export()

    def text_input_active(self):
        """Checks if any 'NormalInput' or 'FloatInput' widgets are currently active (being typed in).
        Returns: True or False
        """

        input_active = False
        for widget in self.walk(restrict=True):
            if widget.__class__.__name__ == 'NormalInput' or widget.__class__.__name__ == 'FloatInput' or widget.__class__.__name__ == 'IntegerInput':
                if widget.focus:
                    input_active = True
                    break
        return input_active

    def has_popup(self):
        """Checks if the popup window is open for this screen.
        Returns: True or False
        """

        if self.popup:
            if self.popup.open:
                return True
        return False

    def dismiss_extra(self):
        """Dummy function, not valid for this screen, but the app calls it when escape is pressed."""
        return False

    def dismiss_popup(self, *_):
        """If this screen has a popup, closes it and removes it."""

        if self.popup:
            self.popup.dismiss()
            self.popup = None

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
                if key == 'enter':
                    self.enter_item()
                    # if self.type != 'None':
                    #     if len(self.photos) > 0:
                    #         app = App.get_running_app()
                    #         app.target = self.selected
                    #         app.photo = ''
                    #         app.fullpath = ''
                    #         app.type = self.type
                    #         app.show_album(button=None)
                if key == 'delete':
                    self.delete()
                if key == 'a':
                    self.toggle_select()
            elif self.popup and self.popup.open:
                if key == 'enter':
                    self.popup.content.dispatch('on_answer', 'yes')

    def enter_item(self):
        photoListRecycleView = self.ids['screenDatabase']
        self.selected_item.visit(photoListRecycleView)

    def previous_album(self):
        """Selects the previous album in the screenDatabase."""
        photoListRecycleView = self.ids['screenDatabase']
        self.selected_item = photoListRecycleView.previous(self.selected_item)
        # new_folder = next_item.displayable_dict()
        # self.displayable = new_folder['displayable']
        # self.type = new_folder['type']
        # self.selected = new_folder['target']
        database_interior = self.ids['databaseInterior']
        database_interior.selected = self.selected_item

        photoListRecycleView.scroll_to_selected()
#        self.on_selected(self.selected_item)
        self.selected_item.visit(photoListRecycleView)

    def next_album(self):
        """Selects the next album in the screenDatabase."""

        photoListRecycleView = self.ids['screenDatabase']
        self.selected_item = photoListRecycleView.next(self.selected_item)
        #new_folder = next_item.displayable_dict()
        #self.displayable = new_folder['displayable']
        #self.type = new_folder['type']
        #self.selected = new_folder['target']

        database_interior = self.ids['databaseInterior']
        database_interior.selected = self.selected_item

        photoListRecycleView.scroll_to_selected()
        #self.on_selected(self.selected_item)
        self.selected_item.visit(photoListRecycleView)

    def show_selected(self):
        """Scrolls the treeview to the currently selected folder"""

        database = self.ids['screenDatabase']
        database_interior = self.ids['databaseInterior']
        selected = self.selected_item
        data = database.data
        current_folder = None
        for i, node in enumerate(data):
            if node.target == selected and node.type == self.type:
                current_folder = node
                break
        if current_folder is not None:
            database_interior.selected = current_folder.dict()
            database.scroll_to_selected()

    def delete(self):
        """Begins the file delete process.  Will call 'delete_selected_confirm' if an album is active."""

        photos = self.ids['photos']
        if photos.selected_nodes:
            self.delete_selected_confirm()

    def delete_selected_confirm(self):
        """Step two of file delete process.  Opens a confirm popup dialog.
        Dialog will call 'delete_selected_answer' on close.
        """

        if self.type == 'Album':
            content = ConfirmPopup(text='Remove Selected Files From The Album "'+self.selected+'"?', yes_text='Remove', no_text="Don't Remove", warn_yes=True)
        elif self.type == 'Tag':
            content = ConfirmPopup(text='Remove The Tag "'+self.selected+'" From Selected Files?', yes_text='Remove', no_text="Don't Remove", warn_yes=True)
        else:
            content = ConfirmPopup(text='Delete The Selected Files?', yes_text='Delete', no_text="Don't Delete", warn_yes=True)
        app = App.get_running_app()
        content.bind(on_answer=self.delete_selected_answer)
        self.popup = NormalPopup(title='Confirm Delete', content=content, size_hint=(None, None), size=(app.popup_x, app.button_scale * 4), auto_dismiss=False)
        self.popup.open()

    def delete_selected_answer(self, instance, answer):
        """Final step of the file delete process, if the answer was 'yes' will delete the selected files.
        Arguments:
            instance: The widget that called this command.
            answer: String, 'yes' if confirm, anything else on deny."""

        del instance
        if answer == 'yes':
            app = App.get_running_app()
            selected_photos = self.get_selected_photos()
            if self.type == 'Tag':
                for photo in selected_photos:
                    self.selected_item.photos.remove(photo)

                app.session.commit()
                app.message("Removed the tag '"+self.selected+"' from "+str(len(selected_photos))+" Files.")
            elif self.type == 'Person':
                for photo in selected_photos:
                    self.selected_item.photos.remove(photo)
                app.session.commit()
                app.message("Removed the person '"+self.selected+"' from "+str(len(selected_photos))+" Files.")
            else:
                folders = []
                errors = []
                deleted_files = 0
                import_to = app.imports[0]['import_to']
                for photo in selected_photos:
                    # must delete files on disk
                    filename = photo.new_full_filename(import_to)
                    if os.path.isfile(filename):
                        try:
                            os.remove(filename)
                            app.session.delete(photo);
                        except Exception as e:
                            error = 'Unable to delete "'+ photo.new_full_filename()
                            errors.append(error)

                if (len(errors)>0):
                    error_text = "\n".join(errors)
                    app.popup_message(text=error_text, title='Error')

                app.session.commit();
                app.message("Deleted "+str(len(selected_photos))+" Files.")

            self.on_selected('', '')
        self.dismiss_popup()
        #self.create_treeview()

    def drop_widget(self, droppedTreeViewItem, position, dropped_type='file', aspect=1):
        """Called when a widget is dropped after being dragged.
        Determines what to do with the widget based on where it is dropped.
        Arguments:
            droppedTreeViewItem: TreeViewItem, object being dragged.
            position: List of X,Y window coordinates that the widget is dropped on.
            dropped_type: String, describes the object being dropped.  May be: 'folder' or 'file'
        """

        app = App.get_running_app()
        folder_list = self.ids['databaseInterior']
        folder_container = self.ids['screenDatabase']
        if folder_container.collide_point(position[0], position[1]):  #check if dropped in the folders list
            #Now, determine exactly what the widget was dropped on
            offset_x, offset_y = folder_list.to_widget(position[0], position[1])
            for widget in folder_list.children:
                if widget.collide_point(position[0], offset_y) and droppedTreeViewItem != widget:
                    if dropped_type == 'folder':
                        if app.database_scanning:
                            app.popup_message("Scanning screenDatabase, can't move folder.", title='Warning')
                            return
                        question = 'Move "'+ droppedTreeViewItem.item.name +'" into "'+ widget.item.name+'"?'
                        content = ConfirmPopup(text=question, yes_text='Move', no_text="Don't Move", warn_yes=True)
                        app = App.get_running_app()
                        content.bind(on_answer=partial(self.move_folder_answer, droppedTreeViewItem.item, widget.item ))
                        self.popup = NormalPopup(title='Confirm Move', content=content, size_hint=(None, None), size=(app.popup_x, app.button_scale * 4), auto_dismiss=False)
                        self.popup.open()
                        return

                    elif dropped_type == 'file':
                        if widget.type != 'None':
                            selected_photos = self.get_selected_photos()
                            # if fullpath not in selected_photos:
                            #     selected_photos.append(fullpath)
                            if app.database_scanning:
                                app.popup_message("Scanning screenDatabase, can't move photo(s).", title='Warning')
                                return
                            widget.data.visit_drop(selected_photos)
                            # if widget.type == 'Tag':
                            #     self.add_to_tag(widget.item, selected_photos=selected_photos)
                            # elif widget.type == 'Person':
                            #     self.add_to_person(widget.target, selected_photos=selected_photos)
                            #     app.popup_message("Adding person "+widget.target+" to selected photos", title='Warning')
                            #
                            # elif widget.type == 'Folder':
                            #     content = ConfirmPopup(text='Move These Files To "'+widget.target+'"?', yes_text="Move", no_text="Don't Move", warn_yes=True)
                            #     content.bind(on_answer=self.move_files)
                            #     self.popup = MoveConfirmPopup(photos=selected_photos, target=widget.target, title='Confirm Move', content=content, size_hint=(None, None), size=(app.popup_x, app.button_scale * 4), auto_dismiss=False)
                            #     self.popup.open()
                            #     pass
                            return

    def move_files(self, instance, answer):
        """Calls the app's move_files command if the dialog was answered with a 'yes'.
        Arguments:
            instance: The button that called this function.
            answer: String, if it is 'yes', the function will activate, if anything else, nothing will happen.
        """

        del instance
        if answer == 'yes':
            app = App.get_running_app()
            app.move_files(self.popup.photos, self.popup.target)
            self.selected = self.popup.target
            #self.create_treeview()
        self.dismiss_popup()

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

    def update_selected(self, *_):
        """Checks if any files are selected in the current album, and updates buttons that only work when files are selected."""

        if not self.ids:
            return

        photos = self.ids['photos']
        if photos.selected_nodes:
            self.photos_selected = True
        else:
            self.photos_selected = False

    def add_favorites(self,selected_photos):
        app = App.get_running_app()
        tag = app.session.query(Tag).filter_by(name='Favorites').first()
        if tag:
            self.add_to_tag(tag,selected_photos)

    def add_to_tag(self, tag, selected_photos=None):
        """Adds a tag to the currently selected photos.
        Arguments:
            tag_name: Tag to add to selected photos.
            selected_photos: List of selected photo data.
        """

        if not selected_photos:
            selected_photos = self.get_selected_photos()
        added_tag = 0
        if tag:
            app = App.get_running_app()
            for photo in selected_photos:
                tag.photos.append(photo)
                added_tag = added_tag + 1

            self.select_none()
            if added_tag:
                if tag.name == 'favorite':
                    self.on_selected()

                app.session.commit()
                #self.create_treeview()
                app.message("Added tag '"+tag.name+"' to "+str(added_tag)+" files.")

    def add_to_person(self, person_name, selected_photos=None):
        """Adds a person to the currently selected photos.
        Arguments:
            person_name: Tag to add to selected photos.
            selected_photos: List of selected photo data.
        """

        if not selected_photos:
            selected_photos = self.get_selected_photos()
        person_name = person_name.strip(' ')
        added_person = 0
        if person_name:
            app = App.get_running_app()
            for photo in selected_photos:
                added = app.Person.add(photo, person_name)
                if added:
                    added_person = added_person + 1
            self.select_none()
            if added_person:
                if person_name == 'favorite':
                    self.on_selected()
                app.photos.commit()
                #self.create_treeview()
                app.message("Added person '"+person_name+"' to "+str(added_person)+" files.")

    # def add_to_person(self, person_name, selected_photos=None):
    #     """Adds the current selected photos to an person.
    #     Arguments:
    #         album_name: String, album to move the photos into.
    #         selected_photos: List of selected photo data.
    #     """
    #
    #     if not selected_photos:
    #         selected_photos = self.get_selected_photos(fullpath=True)
    #     app = App.get_running_app()
    #     added = 0
    #     for person in app.persons:
    #         if person['name'] == person_name:
    #             for photo in selected_photos:
    #                 if photo not in person['photos']:
    #                     person['photos'].append(photo)
    #                     added = added + 1
    #             app.person_save(person)
    #     self.select_none()
    #     if added:
    #         app.message("Added " + str(added) + " files to the person '" + person_name + "'")
    #         self.create_treeview()

    def add_to_tag_menu(self, instance):
        self.add_to_tag(instance.item)
        self.tag_menu.dismiss()

    def show_provinces(self, instance):
        self.add_to_tag(instance.item)
        self.tag_menu.dismiss()

    def add_to_person_menu(self, instance):
        self.add_to_person(instance.text)
        self.person_menu.dismiss()

    def can_add_tag(self, tag_name):
        """Checks if a new tag can be created.
        Argument:
            tag_name: The tag name to check.
        Returns: True or False.
        """

        app = App.get_running_app()
        tag = app.session.query(Tag).filter_by(name=tag_name)
        if tag_name and (tag is not None) and (tag.name.lower() != 'favorites'):
            return True
        else:
            return False

    def can_add_person(self, person_name):
        """Checks if a new person can be created.
        Argument:
            person_name: The person name to check.
        Returns: True or False.
        """

        app = App.get_running_app()
        person_name = person_name.lower().strip(' ')
        persons = app.persons
        if person_name and (person_name not in persons) and (person_name.lower() != 'favorite'):
            return True
        else:
            return False



    def add_person(self, instance=None, answer="yes"):
        """Adds the current input person to the app persons."""
        if answer == "yes":
            if instance is not None:
                person_name = instance.ids['input'].text.lower().strip(' ')
                if not person_name:
                    self.dismiss_popup()
                    return
            else:
                person_input = self.ids['input']
                person_name = person_input.text.lower().strip(' ')
                person_input.text = ''
            app = App.get_running_app()
            app.Person.create(person_name)
            self.create_treeview()
        self.dismiss_popup()

    def can_add_album(self, album_name):
        """Checks if a new album can be created.
        Argument:
            album_name: The album name to check.
        Returns: True or False.
        """

        app = App.get_running_app()
        albums = app.albums
        album_name = album_name.strip(' ')
        if not album_name:
            return False
        for album in albums:
            if album['name'].lower() == album_name.lower():
                return False
        return True

    def accept(self, visitor):
        visitor.item.visit(self)

    def toggle_expanded_folder(self, folder):
        if folder in self.expanded_folders:
            self.expanded_folders.remove(folder)
        else:
            self.expanded_folders.append(folder)
      #  self.create_treeview()

    def create_treeview(self, *_):
        """Create the treeview's data"""

        if not self.ids:
            return

        database = self.ids['screenDatabase']
        database.data = []
        self.__append_treeview_items(database.data)

        self.show_selected()

    def __expand_selected_folder(self,root_folders,data):

        # ensure that selected folder is expanded up to
        selected_folder = self.selected
        while os.path.sep in selected_folder:
            selected_folder, leaf = selected_folder.rsplit(os.path.sep, 1)
            if selected_folder not in self.expanded_folders:
                self.expanded_folders.append(selected_folder)

        if self.search_text:
            folder_data = self.populate_folders(root_folders, root_folders, all=True)
            searched = []
            for item in folder_data:
                if self.search_text.lower() in item['folder_name'].lower() or self.search_text in item['subtext'].lower():
                    searched.append(item)
            folder_data = searched
        else:
            folder_data = self.populate_folders(root_folders, self.expanded_folders)
        data = data + folder_data

        return data

    def update_gps(self):
        app = App.get_running_app()

        for folder in app.session.query(Folder).all():
            longitude = 0
            latitude = 0
            nb_photos = 0
            for photo in folder.photos:
                if photo.longitude:
                    longitude += photo.longitude
                    latitude += photo.latitude
                    nb_photos += 1
            if nb_photos != 0:
                folder.longitude = longitude / nb_photos
                folder.latitude = latitude / nb_photos
                folder.nb_photos = nb_photos
        app.session.commit()


        for country in app.session.query(Country).all():
            country_latitude = 0
            country_longitude = 0
            country_nb_photos = 0
            for province in country.provinces:
                province_latitude = 0
                province_longitude = 0
                province_nb_photos = 0
                for locality in province.localities:
                    locality_longitude = 0
                    locality_latitude = 0
                    locality_nb_photos = 0
                    for place in locality.places:
                        longitude = 0
                        latitude = 0
                        nb_photos = 0
                        for photo in place.photos:
                            if photo.longitude:
                                longitude += photo.longitude
                                latitude += photo.latitude
                                nb_photos +=1
                        if nb_photos != 0:
                            place.longitude = longitude / nb_photos
                            place.latitude = latitude / nb_photos
                            place.nb_photos  = nb_photos


                            locality_longitude += place.longitude
                            locality_latitude += place.latitude
                            locality_nb_photos += place.nb_photos

                    if locality_nb_photos != 0:
                        locality.latitude = locality_latitude / locality_nb_photos
                        locality.longitude = locality_longitude / locality_nb_photos
                        locality.nb_photos = locality_nb_photos

                        province_latitude += locality.latitude
                        province_longitude += locality.longitude
                        province_nb_photos += locality.nb_photos

                if province_nb_photos != 0:
                    province.latitude = province_latitude / province_nb_photos
                    province.longitude = province_longitude / province_nb_photos
                    province.nb_photos = province_nb_photos

                    country_longitude += province.longitude
                    country_latitude += province.latitude
                    country_nb_photos += province.nb_photos

            if country_nb_photos != 0:
                country.latitude = country_latitude / country_nb_photos
                country.longitude = country_longitude / country_nb_photos
                country.nb_photos = country_nb_photos

        app.session.commit()




    def __append_treeview_items(self, data):x
        app = App.get_running_app()

        favorites = Favorites()
        favorites_item =TreeViewItemFavorites(self, favorites, app.button_scale )
        data.append(favorites_item)

        tags = Tags()
        tags_item = TreeViewItemTags(self,tags,app.button_scale)
        data.append(tags_item)

        photosWithNoPlace = DaysOfPhotosWithoutPlace()
        photosWithNoPlace_root = TreeViewItemDaysOfPhotosWithoutPlace(self, photosWithNoPlace, app.button_scale)
        data.append(photosWithNoPlace_root)

        countries = Countries()
        country_root = TreeViewItemCountries(self, countries, app.button_scale)
        data.append(country_root)

        folders = Folders()
        folders_item = TreeViewItemFolders(self,folders,app.button_scale)
        data.append(folders_item)

        faces = Faces()
        faces_item = TreeViewItemFaces(self,faces,app.button_scale)
        data.append(faces_item)

        persons = Persons()
        persons_item = TreeViewItemPersons(self,persons,app.button_scale)
        data.append(persons_item)

       # from models.Videos import Videos


    def populate_folders(self, folder_root, expanded, all=False):
        app = App.get_running_app()
        folders = []
        folder_root = self.sort_folders(folder_root)
        for folder in folder_root:
            full_folder = folder['full_folder']
            subtext = folder['title']
            expandable = True if len(folder['children']) > 0 else False
            is_expanded = True if full_folder in expanded else False
            if all:
                is_expanded = True
            height = app.button_scale * (1.5 if subtext else 1),
            folder_element = TreeViewItemFolder(self,folder,height,expandable,is_expanded)

            folders.append(folder_element)
            if is_expanded:
                if len(folder['children']) > 0:
                    more_folders = self.populate_folders(folder['children'], expanded)
                    folders = folders + more_folders
                    folders[-1]['end'] = True
                    folders[-1]['height'] = folders[-1]['height'] + int(app.button_scale * 0.1)
        return folders

    def sort_folders(self, sort_folders):
        try:
            if self.sort_method in ['Amount', 'Title', 'Imported', 'Modified']:
                app = App.get_running_app()
                folders = []
                for folder in sort_folders:
                    sortby = 0
                    folderpath = folder['full_folder']
                    if self.sort_method == 'Amount':
                        sortby = len(app.Photo.by_folder(folderpath))
                    elif self.sort_method == 'Title':
                        folderinfo = app.Folder.exist(folderpath)
                        if folderinfo:
                            sortby = folderinfo[1]
                        else:
                            sortby = folderpath
                    elif self.sort_method == 'Imported':
                        folder_photos = app.Photo.by_folder(folderpath)
                        for folder_photo in folder_photos:
                            if folder_photo[Photo.IMPORTDATE] > sortby:
                                sortby = folder_photo[Photo.IMPORTDATE]
                    elif self.sort_method == 'Modified':
                        folder_photos = app.Photo.by_folder(folderpath)
                        for folder_photo in folder_photos:
                            if folder_photo[Photo.MODIFYDATE] > sortby:
                                sortby = folder_photo[Photo.MODIFYDATE]

                    folders.append([sortby, folder])
                sorted_folders = sorted(folders, key=lambda x: x[0], reverse=self.sort_reverse)
                sorts, all_folders = zip(*sorted_folders)
            else:
                all_folders = sorted(sort_folders, key=lambda x: x['folder'], reverse=self.sort_reverse)

        except:
            all_folders = sorted_folders

        return all_folders

    def get_folders(self, *_):
        if self.update_folders:
            app = App.get_running_app()
            self.folders = app.Photo.get_folder_treeview_info()  #Just used to cache folder data when a refresh is not needed for a faster refresh
            self.update_folders = False
        return self.folders





    def new_person(self):
        """Starts the new person process, creates an input text popup."""

        content = InputPopup(hint='Person Name', text='Enter A Person:')
        app = App.get_running_app()
        content.bind(on_answer=self.add_person)
        self.popup = NormalPopup(title='Create Person', content=content, size_hint=(None, None),
                                 size=(app.popup_x, app.button_scale * 5), auto_dismiss=False)
        self.popup.open()

    # def new_album(self):
    #     """Starts the new album process, creates an input text popup."""
    #
    #     content = InputPopup(hint='Album Name', text='Enter An Album Name:')
    #     app = App.get_running_app()
    #     content.bind(on_answer=self.add_album)
    #     self.popup = NormalPopup(title='Create Album', content=content, size_hint=(None, None), size=(app.popup_x, app.button_scale * 5), auto_dismiss=False)
    #     self.popup.open()

    def add_folder(self):
        """Starts the add folder process, creates an input text popup."""

        content = InputPopup(hint='Folder Name', text='Enter A Folder Name:')
        app = App.get_running_app()
        content.bind(on_answer=self.add_folder_answer)
        self.popup = NormalPopup(title='Create Folder', content=content, size_hint=(None, None), size=(app.popup_x, app.button_scale * 5), auto_dismiss=False)
        self.popup.open()

    def add_folder_answer(self, instance, answer):
        """Tells the app to rename the folder if the dialog is confirmed.
        Arguments:
            instance: The dialog that called this function.
            answer: String, if 'yes', the folder will be created, all other answers will just close the dialog.
        """

        if answer == 'yes':
            text = instance.ids['input'].text.strip(' ')
            if text:
                app = App.get_running_app()
                app.Folder.add(text)
                self.update_folders = True
        self.dismiss_popup()
       # self.create_treeview()



    def delete_folder_answer(self, instance, answer):
        """Tells the app to delete the folder if the dialog is confirmed.
        Arguments:
            instance: The dialog that called this function.
            answer: String, if 'yes', the folder will be deleted, all other answers will just close the dialog.
        """
        del instance
        if answer == 'yes':
            app = App.get_running_app()
            delete_type = self.type
            delete_item = self.selected
            if delete_type == 'Tag':
                app.Tag.delete(delete_item)
            elif delete_type == 'Person':
                app.Person.remove(delete_item)
            elif delete_type == 'Folder':
                app.Folder.delete(delete_item)
            self.previous_album()
            self.update_folders = True
        self.dismiss_popup()
       # self.create_treeview()

    def move_folder_answer(self, folder, move_to, instance, answer):
        """Tells the app to move the folder if the dialog is confirmed.
        Arguments:
            folder: String, the path of the folder to be moved.
            move_to: String, the path to move the folder into.
            instance: The dialog that called this function.
            answer: String, if 'yes', the folder will be moved, all other answers will just close the dialog.
        """

        del instance
        if answer == 'yes':
            app = App.get_running_app()
            app.move_folder(folder, move_to)
            self.previous_album()
            self.update_folders = True
        self.dismiss_popup()
        #self.create_treeview()

    def on_selected(self, selected_treeViewItem):
        """Called when the selected folder/album/tag is changed.
        Clears and draws the photo list.
        """
        app = App.get_running_app()


        if self.parent and self.ids:
            self.selected_item = selected_treeViewItem
            #dragable = False
            #photos_area = self.ids['photos']
            #photos_area.clear_selection()
            app = App.get_running_app()

            folder_title_type = self.ids['folderType']
            folder_title_type.text = selected_treeViewItem.item.__class__.__name__

            folder_details = self.ids['folderDetails']
            folder_details.clear_widgets()
            folder_details.add_widget(self.album_details)

            folder_path = self.ids['folderPath']
            folder_path.text = selected_treeViewItem.item.name2() if hasattr(selected_treeViewItem.item,'name2') else selected_treeViewItem.item.name

            operation_label = self.ids['operationType']
            operation_label.text = folder_path.text

            Cache.remove('kv.loader')
            photos = []
            delete_button = self.ids['deleteButton']
            delete_button.text = 'Delete me'

            #app.config.set("Settings", "viewtype", self.type)
            #app.config.set("Settings", "viewtarget", self.selected)
            #app.config.set("Settings", "viewdisplay/able", self.displayable)


            self.can_new_folder = selected_treeViewItem.can_new_folder
            self.can_rename_folder = selected_treeViewItem.can_rename_folder
            self.can_delete_folder = selected_treeViewItem.can_delete_folder

            self.update_can_browse()
            self.update_selected()

    def resort_method(self, method):
        """Sets the screenDatabase sort method.
        Argument:
            method: String, the sort method to set.
        """

        self.sort_method = method
        app = App.get_running_app()
        app.config.set('Sorting', 'database_sort', method)
        self.update_folders = True
        #self.create_treeview()

    def resort_reverse(self, reverse):
        """Sets the screenDatabase sort reverse.
        Argument:
            reverse: String, if 'down', reverse will be enabled, disabled on any other string.
        """

        app = App.get_running_app()
        sort_reverse = True if reverse == 'down' else False
        app.config.set('Sorting', 'database_sort_reverse', sort_reverse)
        self.sort_reverse = sort_reverse
        self.update_folders = True
        #self.create_treeview()

    def album_resort_method(self, method):
        """Sets the album sort method.
        Argument:
            method: String, the sort method to use
        """

        self.album_sort_method = method
        app = App.get_running_app()
        app.config.set('Sorting', 'album_sort', method)
        self.on_selected('', '')

    def album_resort_reverse(self, reverse):
        """Sets the album sort reverse.
        Argument:
            reverse: String, if 'down', reverse will be enabled, disabled on any other string.
        """

        app = App.get_running_app()
        album_sort_reverse = True if reverse == 'down' else False
        app.config.set('Sorting', 'album_sort_reverse', album_sort_reverse)
        self.album_sort_reverse = album_sort_reverse
        self.on_selected('', '')

    def on_enter(self, *_):
        """Called when the screen is entered.
        Sets up variables and widgets, and gets the screen ready to be filled with information."""

        app = App.get_running_app()
        try:
            self.scale = float(app.config.get("Settings", "databasescale"))/100
        except:
            self.scale = 1
        if self.scale < self.scale_min:
            self.scale = self.scale_min
        if self.scale > self.scale_max:
            self.scale = self.scale_max
        app.fullpath = ''
        self.tag_menu = NormalDropDown()
        self.album_menu = NormalDropDown()
        self.person_menu = NormalDropDown()
        self.ids['leftpanel'].width = app.left_panel_width()

        #self.can_export = False
        self.folder_details = FolderDetails(owner=self)
        self.album_details = AlbumDetails(owner=self)

        #Set up screenDatabase sorting
        self.sort_dropdown = DatabaseSortDropDown()
        self.sort_dropdown.bind(on_select=lambda instance, x: self.resort_method(x))
        self.sort_method = app.config.get('Sorting', 'database_sort')
        self.sort_reverse = to_bool(app.config.get('Sorting', 'database_sort_reverse'))

        # #Set up album sorting
        # self.album_sort_dropdown = AlbumSortDropDown()
        # self.album_sort_dropdown.bind(on_select=lambda instance, x: self.album_resort_method(x))
        # self.album_sort_method = app.config.get('Sorting', 'album_sort')
        # self.album_sort_reverse = to_bool(app.config.get('Sorting', 'album_sort_reverse'))

        self.update_folders = True
        self.create_treeview()
        #self.on_selected()




class DatabaseOptions(BoxLayout):
    height_scale = NumericProperty(0)
    can_new_folder = BooleanProperty(False)
    can_rename_folder = BooleanProperty(False)
    can_delete_folder = BooleanProperty(False)
    search_text = StringProperty('')
    database = ObjectProperty()

    def set_hidden(self, state):
        app = App.get_running_app()
        if state == 'down':
            if app.animations:
                anim = Animation(height_scale=1, duration=app.animation_length)
                anim.start(self)
            else:
                self.height_scale = 1
        else:
            if app.animations:
                anim = Animation(height_scale=0, duration=app.animation_length)
                anim.start(self)
            else:
                self.height_scale = 0


