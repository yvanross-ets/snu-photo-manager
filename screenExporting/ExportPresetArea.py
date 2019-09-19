import os

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image as KivyImage

from filebrowser import FileBrowser
from generalconstants import scale_size_to_options
from generalElements.MenuButton import MenuButton
from generalElements.NormalDropDown import NormalDropDown
from generalElements.NormalPopup import NormalPopup
from screenExporting.WatermarkSettings import WatermarkSettings
from screenExporting.ScaleSettings import ScaleSettings
from screenExporting.FTPToggleSettings import FTPToggleSettings
from screenExporting.FolderToggleSettings import FolderToggleSettings
from kivy.lang.builder import Builder

Builder.load_string("""
<ExportPresetArea>:
    cols: 1
    height: self.minimum_height
    size_hint: 1, None
    GridLayout:
        height: app.button_scale
        cols: 3
        size_hint_y: None
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            ShortLabel:
                text: 'Title: '
            NormalInput:
                id: titleEditor
                input_filter: app.test_album
                multiline: False
                text: root.name
                on_focus: root.set_title(self)
        MediumBufferX:
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            ShortLabel:
                text: 'Ignore Tags: '
            NormalInput:
                id: ignoreTags
                input_filter: root.test_tags
                multiline: False
                text: root.ignore_tags
                on_focus: root.set_ignore_tags(self)
    GridLayout:
        cols: 3
        size_hint_y: None
        height: app.button_scale
        NormalToggle:
            size_hint_x: 1
            state: 'down' if root.create_subfolder == True else 'normal'
            text: 'Create Subfolder' if root.create_subfolder == True else "Don't Create Subfolder"
            on_press: root.set_create_subfolder(self.state)
        NormalToggle:
            size_hint_x: 1
            state: 'down' if root.export_info == True else 'normal'
            text: 'Export Photo Info' if root.export_info == True else "Don't Export Info"
            on_press: root.set_export_info(self.state)
        NormalToggle:
            size_hint_x: 1
            state: 'down' if root.export_videos == True else 'normal'
            text: 'Export Videos' if root.export_videos == True else "Don't Export Videos"
            on_press: root.set_export_videos(self.state)
    SmallBufferY:

    GridLayout:
        cols: 2
        size_hint_y: None
        height: app.button_scale
        BoxLayout:
            orientation: 'horizontal'
            size_hint_x: 1
            ShortLabel:
                text: 'Export To: '
            NormalToggle:
                toggle: False
                size_hint_x: 1
                id: toggleFolder
                text: 'Folder'
                group: 'exports'
                on_press: root.toggle_exports(self)
                background_normal: 'data/buttontop.png'
                background_down: 'data/buttontop.png'
            NormalToggle:
                toggle: False
                size_hint_x: 1
                id: toggleFTP
                text: 'FTP'
                group: 'exports'
                on_press: root.toggle_exports(self)
                background_normal: 'data/buttontop.png'
                background_down: 'data/buttontop.png'
        BoxLayout:
            size_hint_x: .33

    GridLayout:
        canvas.before:
            Color:
                rgba: app.theme.button_down
            BorderImage:
                size: self.size
                pos: self.pos
                source: 'data/tabbg.png'
        padding: app.padding
        id: toggleSettings
        cols: 1
        size_hint_y: None
        height: self.minimum_height
    SmallBufferY:

    GridLayout:
        cols: 3
        size_hint_y: None
        height: app.button_scale
        NormalToggle:
            toggle: False
            size_hint_x: .33
            state: 'down' if root.scale_image else 'normal'
            text: 'Scale Photo' if root.scale_image else "Don't Scale Photo"
            on_press: root.set_scale_image(self.state)
            background_normal: 'data/button.png'
            background_down: 'data/buttontop.png'
        BoxLayout:
            size_hint_x: .67
    GridLayout:
        cols: 1
        id: scaleSettings
        height: self.minimum_height
        size_hint_y: None
    SmallBufferY:

    GridLayout:
        cols: 3
        size_hint_y: None
        height: app.button_scale
        NormalToggle:
            toggle: False
            size_hint_x: .33
            state: 'down' if root.watermark else 'normal'
            text: 'Use Watermark' if root.watermark else "Don't Use Watermark"
            on_press: root.set_watermark(self.state)
            background_normal: 'data/button.png'
            background_down: 'data/buttontop.png'
        BoxLayout:
            size_hint_x: .67
    GridLayout:
        cols: 1
        id: watermarkSettings
        height: self.minimum_height
        size_hint_y: None
""")

class ExportPresetArea(GridLayout):
    """Widget for displaying and editing settings for an export preset."""

    owner = ObjectProperty()
    name = StringProperty('')
    export_folder = StringProperty('')
    last_export_folder = StringProperty('')
    create_subfolder = BooleanProperty(True)
    export_info = BooleanProperty(True)
    scale_image = BooleanProperty(False)
    scale_size = NumericProperty(1000)
    scale_size_to = StringProperty('long')
    jpeg_quality = NumericProperty(90)
    watermark = BooleanProperty(False)
    watermark_image = StringProperty()
    watermark_opacity = NumericProperty(50)
    watermark_horizontal = NumericProperty(80)
    watermark_vertical = NumericProperty(20)
    watermark_size = NumericProperty(25)
    export_videos = BooleanProperty(False)
    ignore_tags = StringProperty()
    scale_size_to_text = StringProperty('Long Side')
    scale_settings = ObjectProperty()
    watermark_settings = ObjectProperty()
    export = StringProperty('folder')
    ftp_address = StringProperty()
    ftp_user = StringProperty()
    ftp_password = StringProperty()
    ftp_passive = BooleanProperty(True)
    ftp_port = NumericProperty(21)
    index = NumericProperty(0)

    def __init__(self, **kwargs):
        super(ExportPresetArea, self).__init__(**kwargs)
        self.scale_size_to_dropdown = NormalDropDown()
        self.scale_size_to_dropdown.basic_animation = True
        self.last_export_folder = self.export_folder
        if self.scale_image:
            self.add_scale_settings()
        if self.watermark:
            self.add_watermark_settings()
        for option in scale_size_to_options:
            menu_button = MenuButton(text=scale_size_to_options[option])
            menu_button.bind(on_release=self.change_scale_to)
            menu_button.target = option
            self.scale_size_to_dropdown.add_widget(menu_button)
        self.add_export_settings()

    def update_preset(self):
        """Updates this export preset in the app."""

        app = App.get_running_app()
        export_preset = {}
        export_preset['name'] = self.name
        export_preset['export'] = self.export
        export_preset['ftp_address'] = self.ftp_address
        export_preset['ftp_user'] = self.ftp_user
        export_preset['ftp_password'] = self.ftp_password
        export_preset['ftp_passive'] = self.ftp_passive
        export_preset['ftp_port'] = self.ftp_port
        export_preset['export_folder'] = self.export_folder
        export_preset['create_subfolder'] = self.create_subfolder
        export_preset['export_info'] = self.export_info
        export_preset['scale_image'] = self.scale_image
        export_preset['scale_size'] = self.scale_size
        export_preset['scale_size_to'] = self.scale_size_to
        export_preset['jpeg_quality'] = self.jpeg_quality
        export_preset['watermark'] = self.watermark
        export_preset['watermark_image'] = self.watermark_image
        export_preset['watermark_opacity'] = self.watermark_opacity
        export_preset['watermark_horizontal'] = self.watermark_horizontal
        export_preset['watermark_vertical'] = self.watermark_vertical
        export_preset['watermark_size'] = self.watermark_size
        ignore_tags = self.ignore_tags.split(',')
        ignore_tags = list(filter(bool, ignore_tags))
        export_preset['ignore_tags'] = ignore_tags
        export_preset['export_videos'] = self.export_videos
        app.exports[self.index] = export_preset
        self.owner.owner.selected_preset = self.index
        app.export_preset_write()

    def toggle_exports(self, button):
        """Switch between folder and ftp export."""

        if button.text == 'FTP':
            self.export = 'ftp'
        else:
            self.export = 'folder'
        self.add_export_settings()
        self.update_preset()

    def add_export_settings(self, *_):
        """Add the proper export settings to the export dialog."""

        if self.export == 'ftp':
            button = self.ids['toggleFTP']
            button.state = 'down'
            toggle_area = self.ids['toggleSettings']
            toggle_area.clear_widgets()
            toggle_area.add_widget(FTPToggleSettings(owner=self))
        else:
            button = self.ids['toggleFolder']
            button.state = 'down'
            toggle_area = self.ids['toggleSettings']
            toggle_area.clear_widgets()
            toggle_area.add_widget(FolderToggleSettings(owner=self))

    def update_test_image(self, *_):
        """Regenerate the watermark preview image."""

        if self.watermark_settings:
            test_image = self.watermark_settings.ids['testImage']
            test_image.clear_widgets()
            if os.path.isfile(self.watermark_image):
                image = KivyImage(source=self.watermark_image)
                size_x = test_image.size[0]*(self.watermark_size/100)
                size_y = test_image.size[1]*(self.watermark_size/100)
                image.size = (size_x, size_y)
                image.size_hint = (None, None)
                image.opacity = self.watermark_opacity/100
                x_pos = test_image.pos[0]+((test_image.size[0] - size_x)*(self.watermark_horizontal/100))
                y_pos = test_image.pos[1]+((test_image.size[1] - size_y)*(self.watermark_vertical/100))
                image.pos = (x_pos, y_pos)
                test_image.add_widget(image)

    def add_watermark_settings(self, *_):
        """Add the watermark settings widget to the proper area."""

        watermark_settings_widget = self.ids['watermarkSettings']
        self.watermark_settings = WatermarkSettings(owner=self)
        watermark_settings_widget.add_widget(self.watermark_settings)
        Clock.schedule_once(self.update_test_image)

    def add_scale_settings(self, *_):
        """Add the scale settings widget to the proper area."""

        scale_settings_widget = self.ids['scaleSettings']
        self.scale_settings = ScaleSettings(owner=self)
        scale_settings_widget.add_widget(self.scale_settings)

    def select_watermark(self):
        """Open a filebrowser to select the watermark image."""

        content = FileBrowser(ok_text='Select', filters=['*.png'])
        content.bind(on_cancel=self.owner.owner.dismiss_popup)
        content.bind(on_ok=self.select_watermark_confirm)
        self.owner.owner.popup = filepopup = NormalPopup(title='Select Watermark PNG Image', content=content, size_hint=(0.9, 0.9))
        filepopup.open()

    def select_watermark_confirm(self, *_):
        """Called when the watermark file browse dialog is closed."""

        self.watermark_image = self.owner.owner.popup.content.filename
        self.owner.owner.dismiss_popup()
        self.update_preset()
        self.update_test_image()

    def set_scale_size(self, instance):
        """Apply the scale size setting, only when the input area loses focus."""

        if not instance.focus:
            self.scale_size = int(instance.text)
            self.update_preset()

    def on_scale_size_to(self, *_):
        self.scale_size_to_text = scale_size_to_options[self.scale_size_to]

    def set_watermark_opacity(self, instance):
        self.watermark_opacity = int(instance.value)
        self.update_preset()
        self.update_test_image()

    def set_watermark_horizontal(self, instance):
        self.watermark_horizontal = int(instance.value)
        self.update_preset()
        self.update_test_image()

    def set_watermark_vertical(self, instance):
        self.watermark_vertical = int(instance.value)
        self.update_preset()
        self.update_test_image()

    def set_watermark_size(self, instance):
        self.watermark_size = int(instance.value)
        self.update_preset()
        self.update_test_image()

    def set_jpeg_quality(self, instance):
        self.jpeg_quality = int(instance.value)
        self.update_preset()

    def change_scale_to(self, instance):
        self.scale_size_to_dropdown.dismiss()
        self.scale_size_to = instance.target
        self.update_preset()

    def set_scale_image(self, state):
        if state == 'down':
            self.scale_image = True
            self.add_scale_settings()
        else:
            self.scale_image = False
            scale_settings_widget = self.ids['scaleSettings']
            scale_settings_widget.clear_widgets()
        self.update_preset()

    def set_export_videos(self, state):
        if state == 'down':
            self.export_videos = True
        else:
            self.export_videos = False
        self.update_preset()

    def set_export_info(self, state):
        if state == 'down':
            self.export_info = True
        else:
            self.export_info = False
        self.update_preset()

    def set_watermark(self, state):
        if state == 'down':
            self.watermark = True
            self.add_watermark_settings()
        else:
            self.watermark = False
            watermark_settings_widget = self.ids['watermarkSettings']
            watermark_settings_widget.clear_widgets()
        self.update_preset()

    def set_create_subfolder(self, state):
        if state == 'down':
            self.create_subfolder = True
        else:
            self.create_subfolder = False
        self.update_preset()

    def test_tags(self, string, *_):
        return "".join(i for i in string if i not in "#%&*{}\\/:?<>+|\"=][;").lower()

    def set_ignore_tags(self, instance):
        if not instance.focus:
            self.ignore_tags = instance.text
            self.update_preset()

    def set_ftp_passive(self, instance):
        if instance.state == 'down':
            self.ftp_passive = True
            instance.text = 'Passive Mode'
        else:
            self.ftp_passive = False
            instance.text = 'Active Mode'
        self.update_preset()

    def set_title(self, instance):
        if not instance.focus:
            self.name = instance.text
            self.update_preset()
            self.owner.text = instance.text

    def filename_filter(self, string, *_):
        remove_string = '\\/*?<>|,'.replace(os.path.sep, "")
        return "".join(i for i in string if i not in remove_string)

    def set_ftp_user(self, instance):
        if not instance.focus:
            self.ftp_user = instance.text
            self.update_preset()

    def set_ftp_password(self, instance):
        if not instance.focus:
            self.ftp_password = instance.text
            self.update_preset()

    def set_ftp_address(self, instance):
        if not instance.focus:
            self.ftp_address = instance.text
            self.update_preset()

    def set_ftp_port(self, instance):
        if not instance.focus:
            self.ftp_port = int(instance.text)
            self.update_preset()

    def ftp_filter(self, string, *_):
        remove_string = '\\:<>| "\''
        return "".join(i for i in string if i not in remove_string).lower()

    def set_export_folder(self, instance):
        if not instance.focus:
            if os.path.exists(instance.text):
                self.export_folder = instance.text
                self.last_export_folder = instance.text
            else:
                instance.text = self.last_export_folder
                self.export_folder = self.last_export_folder
            self.update_preset()

    def select_export(self):
        """Activates a popup folder browser dialog to select the export folder."""

        content = FileBrowser(ok_text='Select', directory_select=True)
        content.bind(on_cancel=self.owner.owner.dismiss_popup)
        content.bind(on_ok=self.select_export_confirm)
        self.owner.owner.popup = filepopup = NormalPopup(title='Select An Export Folder', content=content, size_hint=(0.9, 0.9))
        filepopup.open()

    def select_export_confirm(self, *_):
        """Called when the export folder select dialog is closed successfully."""

        self.export_folder = self.owner.owner.popup.content.filename
        self.owner.owner.dismiss_popup()
        self.update_preset()