import os
from PIL import Image
import datetime
from shutil import copy2
import time
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from io import BytesIO
import threading

from generalconstants import *
from generalElements.popups.ScanningPopup import ScanningPopup
from generalElements.dropDowns.AlbumSortDropDown import AlbumSortDropDown
from generalcommands import to_bool

from kivy.lang.builder import Builder

from screenExporting.ExportPreset import ExportPreset

Builder.load_string("""
<ScreenExporting>:
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
            HeaderLabel:
                text: 'Export Photos'
            InfoLabel:
            DatabaseLabel:
            SettingsButton:
        BoxLayout:
            orientation: 'horizontal'
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: .5
                Header:
                    NormalLabel:
                        text: 'Select An Export Preset:'
                    NormalButton:
                        id: newPresetButton
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
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: .5
                Header:
                    MediumBufferX:
                    LeftNormalLabel:
                        text: 'Select Photos To Export: ' + root.target
                    MediumBufferX:
                    ShortLabel:
                        text: 'Sort By:'
                    MenuStarterButton:
                        size_hint_x: 1
                        id: sortButton
                        text: root.sort_method
                        on_release: root.sort_dropdown.open(self)
                    ReverseToggle:
                        id: sortReverseButton
                        state: root.sort_reverse_button
                        on_press: root.resort_reverse(self.state)
                    MediumBufferX:
                    NormalButton:
                        text: 'Toggle Select'
                        on_release: root.toggle_select()
                MainArea:
                    NormalRecycleView:
                        id: photosContainer
                        viewclass: 'PhotoRecycleThumb'
                        SelectableRecycleGrid:
                            id: photos




""")


class ScreenExporting(Screen):
    popup = None
    sort_dropdown = ObjectProperty()
    sort_method = StringProperty()
    sort_reverse = BooleanProperty(False)
    target = StringProperty()
    type = StringProperty()
    photos_selected = BooleanProperty(False)
    photos = []
    cancel_exporting = BooleanProperty(False)
    total_export_files = NumericProperty(0)
    exported_files = NumericProperty(0)
    total_export = NumericProperty(0)
    exported_size = NumericProperty(0)
    current_upload_blocks = NumericProperty(0)
    exporting = BooleanProperty(False)
    export_start_time = NumericProperty(0)
    scanningthread = None  #Holder for the exporting process thread.
    ftp = None
    sort_reverse_button = StringProperty('normal')
    selected_preset = NumericProperty(-1)

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

    def on_sort_reverse(self, *_):
        """Updates the sort reverse button's state variable, since kivy doesnt just use True/False for button states."""

        app = App.get_running_app()
        self.sort_reverse_button = 'down' if to_bool(app.config.get('Sorting', 'album_sort_reverse')) else 'normal'

    def can_export(self):
        return self.photos_selected

    def dismiss_extra(self):
        """Dummy function, not valid for this screen, but the app calls it when escape is pressed."""
        return False

    def resort_method(self, method):
        """Sets the album sort method.
        Argument:
            method: String, the sort method to use
        """

        self.sort_method = method
        app = App.get_running_app()
        app.config.set('Sorting', 'album_sort', method)
        self.update_photolist()

    def resort_reverse(self, reverse):
        """Sets the album sort reverse.
        Argument:
            reverse: String, if 'down', reverse will be enabled, disabled on any other string.
        """

        app = App.get_running_app()
        sort_reverse = True if reverse == 'down' else False
        app.config.set('Sorting', 'album_sort_reverse', sort_reverse)
        self.sort_reverse = sort_reverse
        self.update_photolist()

    def toggle_select(self):
        """Select all files, or unselect all selected files."""

        photos = self.ids['photos']
        photos.toggle_select()
        self.update_selected()

    def select_all(self):
        photos = self.ids['photos']
        photos.select_all()
        self.update_selected()

    def update_selected(self):
        """Checks if any viewed photos are selected."""

        photos = self.ids['photos']
        if photos.selected_nodes:
            selected = True
        else:
            selected = False
        self.photos_selected = selected

    def on_enter(self):
        """Called when this screen is entered.  Sets up widgets and gets the photo list."""

        self.selected_preset = -1
        app = App.get_running_app()
        self.exporting = False
        self.sort_dropdown = AlbumSortDropDown()
        self.sort_dropdown.bind(on_select=lambda instance, x: self.resort_method(x))
        self.sort_method = app.config.get('Sorting', 'album_sort')
        self.sort_reverse = to_bool(app.config.get('Sorting', 'album_sort_reverse'))
        self.target = app.export_target
        self.type = app.export_type

        #Get photos
        self.photos = []
        if self.type == 'Album':
            for albuminfo in app.albums:
                if albuminfo['name'] == self.target:
                    photo_paths = albuminfo['photos']
                    for fullpath in photo_paths:
                        photoinfo = app.Photo.exist(fullpath)
                        if photoinfo:
                            self.photos.append(photoinfo)
        elif self.type == 'Tag':
            self.photos = app.Tag.photos(self.target)
        else:
            self.photos = app.Photo.by_folder(self.target)

        self.update_treeview()
        self.update_photolist()
        photos = self.ids['photos']
        photos.select_all()
        self.update_selected()

    def update_photolist(self, select=True):
        """Clears and refreshes the grid view of photos."""

        #sort photo list
        if self.sort_method == 'Imported':
            sorted_photos = sorted(self.photos, key=lambda x: x[6], reverse=self.sort_reverse)
        elif self.sort_method == 'Modified':
            sorted_photos = sorted(self.photos, key=lambda x: x[7], reverse=self.sort_reverse)
        elif self.sort_method == 'Owner':
            sorted_photos = sorted(self.photos, key=lambda x: x[11], reverse=self.sort_reverse)
        elif self.sort_method == 'Name':
            sorted_photos = sorted(self.photos, key=lambda x: os.path.basename(x[0]), reverse=self.sort_reverse)
        else:
            sorted_photos = sorted(self.photos, key=lambda x: x[0], reverse=self.sort_reverse)

        #Create photo widgets
        photos_container = self.ids['photosContainer']
        datas = []
        for photo in sorted_photos:
            full_filename = os.path.join(photo[2], photo[0])
            tags = photo[8].split(',')
            favorite = True if 'favorite' in tags else False
            fullpath = photo[0]
            database_folder = photo[2]
            video = os.path.splitext(full_filename)[1].lower() in movietypes
            data = {
                'fullpath': fullpath,
                'photoinfo': photo,
                'folder': self.target,
                'database_folder': database_folder,
                'filename': full_filename,
                'target': self.target,
                'type': self.type,
                'owner': self,
                'favorite': favorite,
                'video': video,
                'photo_orientation': photo[13],
                'source': full_filename,
                'temporary': False,
                'selected': False,
                'selectable': True,
                'dragable': False,
                'view_album': False
            }
            datas.append(data)
        photos_container.data = datas
        if select:
            self.select_all()

    def on_leave(self):
        """Called when the screen is left, clean up data."""

        presets = self.ids['presets']
        presets.clear_widgets()
        photo_container = self.ids['photosContainer']
        photo_container.data = []

    def update_treeview(self):
        """Clears and populates the export presets list on the left side."""

        app = App.get_running_app()
        presets = self.ids['presets']

        #Clear old presets
        presets.clear_widgets()

        #Populate export presets nodes
        for index, export_preset in enumerate(app.exports):
            preset = ExportPreset(index=index, text=export_preset['name'], data=export_preset, owner=self)
            if index == self.selected_preset:
                preset.expanded = True
            presets.add_widget(preset)

    def cancel_export(self, *_):
        """Signal to stop the exporting process.  Will also try to close the ftp connection if it exists."""

        self.cancel_exporting = True
        try:
            self.ftp.close()
        except:
            pass

    def export(self):
        """Begins the export process.  Opens a progress dialog, and starts the export thread."""

        self.ftp = False
        app = App.get_running_app()
        preset = app.exports[self.selected_preset]
        if preset['export'] == 'ftp':
            if not preset['ftp_address']:
                app.message(text="Please Set Export Location")
                return
        else:
            if not preset['export_folder']:
                app.message(text="Please Set Export Location")
                return
        if not self.photos_selected:
            app.message(text="Please Select Photos To Export")
            return
        self.cancel_exporting = False
        self.popup = ScanningPopup(title='Exporting Files', auto_dismiss=False, size_hint=(None, None), size=(app.popup_x, app.button_scale * 4))
        self.popup.open()
        scanning_button = self.popup.ids['scanningButton']
        scanning_button.bind(on_release=self.cancel_export)
        self.scanningthread = threading.Thread(target=self.exporting_process)
        self.scanningthread.start()

    def update_percentage(self, *_):
        """Updates the exporting process percentage value in the exporting dialog."""

        self.current_upload_blocks = self.current_upload_blocks + 1
        file_completed = (8192*self.current_upload_blocks)
        percent_completed = int(100*((self.exported_size+file_completed)/self.total_export))
        self.popup.scanning_percentage = percent_completed
        time_taken = time.time() - self.export_start_time
        if percent_completed > 0:
            total_time = (100/percent_completed)*time_taken
            time_remaining = total_time - time_taken
            str(datetime.timedelta(seconds=time_remaining))
            remaining = ', '+str(datetime.timedelta(seconds=int(time_remaining)))+' Remaining'
        else:
            remaining = ''
        self.popup.scanning_text = 'Uploading: '+str(self.exported_files)+' out of '+str(self.total_export_files)+' files'+remaining

    def exporting_process(self):
        """Handles exporting the files.  This should be in a different thread so the interface can still respond."""

        self.exporting = True
        app = App.get_running_app()
        preset = app.exports[self.selected_preset]

        #Get photo list
        ignore_tags = preset['ignore_tags']
        exported_photos = 0
        selected_photos = self.get_selected_photos()
        photos = []
        for photo in selected_photos:
            if photo[12] != 0:
                ignore_file = False
                if ignore_tags:
                    for tag in ignore_tags:
                        photo_tags = photo[8].split(',')
                        if tag in photo_tags:
                            ignore_file = True
                if not preset['export_videos']:
                    path, extension = os.path.splitext(photo[0])
                    if extension.lower() in movietypes:
                        ignore_file = True
                if not ignore_file:
                    photos.append(photo)

        if not photos:
            return

        #determine export filenames (prevent any duplicate filenames)
        export_photos = []
        for photo in photos:
            photo_filename = os.path.basename(photo[0])
            basename, extension = os.path.splitext(photo_filename)
            test_name = photo_filename
            add_number = 0
            while test_name in export_photos:
                add_number = add_number+1
                test_name = basename+"("+str(add_number)+")"+extension
            export_photos.append(test_name)

        if self.type == 'tag':
            subfolder = 'Photos Tagged As '+self.target.title()
        else:
            subfolder = os.path.split(self.target)[1]

        #ftp export mode
        if preset['export'] == 'ftp':
            subfolder = subfolder.replace("'", "").replace("/", " - ").replace("\\", " - ")
            if '/' in preset['ftp_address']:
                ftp_host, ftp_folder = preset['ftp_address'].split('/', 1)
                ftp_folder = ftp_folder.strip('/')
            else:
                ftp_host = preset['ftp_address']
                ftp_folder = ''
            from ftplib import FTP
            try:
                self.ftp = ftp = FTP()
                self.popup.scanning_text = 'Connecting To FTP...'
                ftp.connect(ftp_host, preset['ftp_port'])
                self.popup.scanning_text = 'Logging In To FTP...'
                ftp.login(preset['ftp_user'], preset['ftp_password'])
                ftp.set_pasv(preset['ftp_passive'])
                self.popup.scanning_text = 'Creating Folders...'
                ftp_filelist = ftp.nlst()

                #set the ftp folder and create if needed
                if ftp_folder:
                    subfolders = ftp_folder.split('/')
                    for folder in subfolders:
                        if folder not in ftp_filelist:
                            ftp.mkd(folder)
                        ftp.cwd(folder)
                        ftp_filelist = ftp.nlst()
                if preset['create_subfolder']:
                    file_list = ftp.nlst()
                    if subfolder not in file_list:
                        ftp.mkd(subfolder)
                    ftp.cwd(subfolder)
                    ftp_filelist = ftp.nlst()

                if preset['export_info']:
                    self.popup.scanning_text = 'Uploading Photo Info...'
                    infofile = os.path.join(".photoinfo.ini")
                    if os.path.exists(infofile):
                        os.remove(infofile)
                    app.save_photoinfo(self.target, '.', '', photos=photos, newnames=export_photos)
                    if '.photoinfo.ini' in ftp_filelist:
                        ftp.delete('.photoinfo.ini')
                    if os.path.exists(infofile):
                        ftp.storbinary("STOR .photoinfo.ini", open(infofile, 'rb'))
                        os.remove(infofile)
                self.total_export = 0
                for photo in photos:
                    photofile = os.path.join(photo[2], photo[0])
                    if os.path.exists(photofile):
                        self.total_export = self.total_export + os.path.getsize(photofile)
                self.popup.scanning_text = 'Uploading '+str(len(photos))+' Files'
                self.exported_size = 0
                self.total_export_files = len(photos)
                self.export_start_time = time.time()
                for index, photo in enumerate(photos):
                    self.exported_files = index+1
                    percent_completed = 100*(self.exported_size/self.total_export)
                    self.popup.scanning_percentage = percent_completed
                    if self.cancel_exporting:
                        self.popup.scanning_text = 'Upload Canceled, '+str(index)+' Files Uploaded'
                        break
                    photofile = os.path.join(photo[2], photo[0])
                    if os.path.exists(photofile):
                        photo_size = os.path.getsize(photofile)
                        extension = os.path.splitext(photofile)[1]
                        photofilename = export_photos[index]
                        #photofilename = os.path.basename(photofile)
                        if photofilename in ftp_filelist:
                            ftp.delete(photofilename)

                        if extension.lower() in imagetypes and (preset['scale_image'] or preset['watermark']):
                            #image needs to be edited in some way
                            imagedata = Image.open(photofile)
                            if imagedata.mode != 'RGB':
                                imagedata = imagedata.convert('RGB')

                            orientation = photo[13]
                            imagedata = app.edit_fix_orientation(imagedata, orientation)

                            if preset['scale_image']:
                                imagedata = app.edit_scale_image(imagedata, preset['scale_size'], preset['scale_size_to'])
                            if preset['watermark']:
                                imagedata = app.edit_add_watermark(imagedata, preset['watermark_image'], preset['watermark_opacity'], preset['watermark_horizontal'], preset['watermark_vertical'], preset['watermark_size'])
                            output = BytesIO()
                            imagedata.save(output, 'JPEG', quality=preset['jpeg_quality'])
                            output.seek(0)
                            self.current_upload_blocks = 0
                            ftp.storbinary("STOR "+photofilename, output, callback=self.update_percentage)
                        else:
                            #image or video should just be uploaded
                            self.current_upload_blocks = 0
                            ftp.storbinary("STOR "+photofilename, open(photofile, 'rb'),
                                           callback=self.update_percentage)
                        exported_photos = exported_photos + 1
                        self.exported_size = self.exported_size+photo_size

                        #check that the file was uploaded
                        ftp_filelist = ftp.nlst()
                        if photofilename not in ftp_filelist:
                            self.cancel_exporting = True
                            self.popup.scanning_text = 'Unable To Upload "'+photo[0]+'".'
                ftp.quit()
                ftp.close()
                self.ftp = False
            except Exception as e:
                if self.cancel_exporting:
                    self.popup.scanning_text = 'Canceled Upload. Partial Files May Be Left On The Server.'
                else:
                    self.cancel_exporting = True
                    self.popup.scanning_text = 'Unable To Upload: '+str(e)

        #local directory export mode
        else:
            if preset['create_subfolder']:
                save_location = os.path.join(preset['export_folder'], subfolder)
            else:
                save_location = preset['export_folder']
            if not os.path.exists(save_location):
                os.makedirs(save_location)
            if preset['export_info']:
                app.save_photoinfo(self.target, save_location, self.type.lower(), photos=photos, newnames=export_photos)
            self.total_export = 0
            for photo in photos:
                photofile = os.path.join(photo[2], photo[0])
                if os.path.exists(photofile):
                    self.total_export = self.total_export + os.path.getsize(photofile)
            self.popup.scanning_text = 'Exporting '+str(len(photos))+' Files'
            self.exported_size = 0
            self.total_export_files = len(photos)
            self.export_start_time = time.time()
            for index, photo in enumerate(photos):
                self.exported_files = index+1
                percent_completed = 100*(self.exported_size/self.total_export)
                self.popup.scanning_percentage = percent_completed
                if self.cancel_exporting:
                    self.popup.scanning_text = 'Export Canceled, '+str(index)+' Files Exported'
                    break
                photofile = os.path.join(photo[2], photo[0])
                if os.path.exists(photofile):
                    photo_size = os.path.getsize(photofile)
                    extension = os.path.splitext(photofile)[1]
                    #photofilename = os.path.basename(photofile)
                    photofilename = export_photos[index]
                    savefile = os.path.join(save_location, photofilename)
                    if os.path.exists(savefile):
                        os.remove(savefile)
                    if extension.lower() in imagetypes and (preset['scale_image'] or preset['watermark']):
                        #image needs to be edited in some way
                        imagedata = Image.open(photofile)
                        if imagedata.mode != 'RGB':
                            imagedata = imagedata.convert('RGB')
                        orientation = photo[13]
                        imagedata = app.edit_fix_orientation(imagedata, orientation)

                        if preset['scale_image']:
                            imagedata = app.edit_scale_image(imagedata, preset['scale_size'], preset['scale_size_to'])
                        if preset['watermark']:
                            imagedata = app.edit_add_watermark(imagedata, preset['watermark_image'], preset['watermark_opacity'], preset['watermark_horizontal'], preset['watermark_vertical'], preset['watermark_size'])
                        imagedata.save(savefile, 'JPEG', quality=preset['jpeg_quality'])
                    else:
                        #image or video should just be copied
                        copy2(photofile, savefile)
                    exported_photos = exported_photos + 1
                    self.exported_size = self.exported_size+photo_size
            self.exporting = False
        if not self.cancel_exporting:
            app.message('Completed Exporting '+str(len(photos))+' files.')
            Clock.schedule_once(self.finish_export)
        else:
            scanning_button = self.popup.ids['scanningButton']
            scanning_button.text = 'OK'
            scanning_button.bind(on_release=self.finish_export)

    def finish_export(self, *_):
        """Closes the export popup and leaves this screen."""

        self.popup.dismiss()
        app = App.get_running_app()
        app.show_database()

    def add_preset(self):
        """Create a new export preset and refresh the preset list."""

        app = App.get_running_app()
        app.export_preset_new()
        self.selected_preset = len(app.exports) - 1
        self.update_treeview()

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

        if self.exporting:
            self.cancel_export()
        else:
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
                if key == 'a':
                    self.toggle_select()


