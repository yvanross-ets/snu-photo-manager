from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.gridlayout import GridLayout

from generalcommands import to_bool
from generalconstants import containers_friendly, video_codecs_friendly, audio_codecs_friendly
from generalElements.buttons.MenuButton import MenuButton
from generalElements.dropDowns.NormalDropDown import NormalDropDown

from kivy.lang.builder import Builder

Builder.load_string("""
<EditConvertVideo>:
    padding: 0, 0, int(app.button_scale / 2), 0
    cols: 1
    size_hint: 1, None
    height: self.minimum_height
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        WideButton:
            text: 'Convert'
            on_release: root.encode()
        WideButton:
            text: 'Cancel Edit'
            warn: True
            on_release: root.owner.set_edit_panel('main')
    MediumBufferY:
    NormalLabel:
        text: 'Convert Video:'
    MenuStarterButtonWide:
        text: 'Presets'
        size_hint_x: 1
        on_release: root.preset_drop.open(self)
    GridLayout:
        canvas.before:
            Color:
                rgba: app.theme.area_background
            BorderImage:
                pos: self.pos
                size: self.size
                source: 'data/buttonflat.png'
        padding: app.padding
        cols: 1
        size_hint: 1, None
        height: self.minimum_height
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            LeftNormalLabel:
                text: 'Container:'
            MenuStarterButtonWide:
                size_hint_x: 1
                text: root.file_format
                on_release: root.container_drop.open(self)
        SmallBufferY:
        NormalToggle:
            id: resize
            size_hint_x: 1
            state: 'down' if root.resize else 'normal'
            text: 'Resize' if self.state == 'down' else 'No Resize'
            on_release: root.update_resize(self.state)
        BoxLayout:
            disabled: not root.resize
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            ShortLabel:
                text: 'Size:'
            NormalInput:
                id: widthInput
                hint_text: '1920'
                multiline: False
                text: root.resize_width
                on_text: root.set_resize_width(self)
            ShortLabel:
                text: 'x'
            NormalInput:
                id: heightInput
                hint_text: '1080'
                multiline: False
                text: root.resize_height
                on_text: root.set_resize_height(self)
        SmallBufferY:
        NormalToggle:
            id: deinterlace
            size_hint_x: 1
            state: 'down' if root.deinterlace else 'normal'
            text: 'Deinterlace' if self.state == 'down' else 'No Deinterlace'
            on_release: root.update_deinterlace(self.state)
        SmallBufferY:
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            LeftNormalLabel:
                text: 'Video Codec:'
            MenuStarterButtonWide:
                size_hint_x: 1
                text: root.video_codec
                on_release: root.video_codec_drop.open(self)
                id: videoCodecDrop
        #BoxLayout:
        #    orientation: 'horizontal'
        #    size_hint_y: None
        #    height: app.button_scale
        #    LeftNormalLabel:
        #        text: 'Video Quality:'
        #    MenuStarterButtonWide:
        #        size_hint_x: 1
        #        text: root.video_quality
        #        on_release: root.video_quality_drop.open(self)
        #        id: videoQualityDrop
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            LeftNormalLabel:
                text: 'Encoding Speed:'
            MenuStarterButtonWide:
                size_hint_x: 1
                text: root.encoding_speed
                on_release: root.encoding_speed_drop.open(self)
                id: encodingSpeedDrop
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            LeftNormalLabel:
                text: 'Video Bitrate:'
            FloatInput:
                id: videoBitrateInput
                text: root.video_bitrate

        SmallBufferY:
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            LeftNormalLabel:
                text: 'Audio Codec:'
            MenuStarterButtonWide:
                size_hint_x: 1
                text: root.audio_codec
                on_release: root.audio_codec_drop.open(self)
                id: audioCodecDrop
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            LeftNormalLabel:
                text: 'Audio Bitrate:'
            FloatInput:
                id: audioBitrateInput
                text: root.audio_bitrate
    SmallBufferY:
    GridLayout:
        canvas.before:
            Color:
                rgba: app.theme.area_background
            BorderImage:
                pos: self.pos
                size: self.size
                source: 'data/buttonflat.png'
        padding: app.padding
        cols: 1
        size_hint: 1, None
        height: self.minimum_height
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            LeftNormalLabel:
                text: "Manual command line:"
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            LeftNormalLabel:
                text: "This will override all other settings."
        SmallBufferY:
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            ShortLabel:
                text: 'ffmpeg.exe '
            NormalInput:
                id: commandInput
                hint_text: '-sn %c %v %a %f %p %b %d'
                multiline: False
                text: root.command_line
                on_text: root.set_command_line(self)
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            LeftNormalLabel:
                text: "String Replacements:"
        GridLayout:
            cols: 3
            size_hint: 1, None
            height: int(app.button_scale * 9)

            ShortLabel:
                text: '%i'
            ShortLabel:
                text: ' - '
            LeftNormalLabel:
                text: 'Input File (Required)'

            ShortLabel:
                text: '%c'
            ShortLabel:
                text: ' - '
            LeftNormalLabel:
                text: 'Container Setting'

            ShortLabel:
                text: '%v'
            ShortLabel:
                text: ' - '
            LeftNormalLabel:
                text: 'Video Codec Setting'

            ShortLabel:
                text: '%a'
            ShortLabel:
                text: ' - '
            LeftNormalLabel:
                text: 'Audio Codec Setting'

            ShortLabel:
                text: '%f'
            ShortLabel:
                text: ' - '
            LeftNormalLabel:
                text: 'Framerate (From Original File)'

            ShortLabel:
                text: '%p'
            ShortLabel:
                text: ' - '
            LeftNormalLabel:
                text: 'Pixel Format (From Original File)'

            ShortLabel:
                text: '%b'
            ShortLabel:
                text: ' - '
            LeftNormalLabel:
                text: 'Video Bitrate Setting'

            ShortLabel:
                text: '%d'
            ShortLabel:
                text: ' - '
            LeftNormalLabel:
                text: 'Audio Bitrate Setting'

            ShortLabel:
                text: '%%'
            ShortLabel:
                text: ' - '
            LeftNormalLabel:
                text: 'Single Percent Sign (%)'
""")

class EditConvertVideo(GridLayout):
    """Convert a video file to another format using ffmpeg."""

    owner = ObjectProperty()

    #Encoding settings
    video_codec = StringProperty()
    audio_codec = StringProperty()
    video_quality = StringProperty()
    encoding_speed = StringProperty()
    file_format = StringProperty()
    input_file = StringProperty()
    video_bitrate = StringProperty('8000')
    audio_bitrate = StringProperty('192')
    command_line = StringProperty()
    deinterlace = BooleanProperty(False)
    resize = BooleanProperty(False)
    resize_width = StringProperty('1920')
    resize_height = StringProperty('1080')

    #Dropdown menus
    preset_drop = ObjectProperty()
    container_drop = ObjectProperty()
    video_codec_drop = ObjectProperty()
    video_quality_drop = ObjectProperty()
    encoding_speed_drop = ObjectProperty()
    audio_codec_drop = ObjectProperty()

    def __init__(self, **kwargs):
        self.setup_dropdowns()
        app = App.get_running_app()
        encoding_preset = app.config.get('Presets', 'encoding')
        if encoding_preset:
            encoding_settings = encoding_preset.split(',', 10)
            if len(encoding_settings) == 11:
                self.file_format = encoding_settings[0]
                self.video_codec = encoding_settings[1]
                self.audio_codec = encoding_settings[2]
                self.resize = to_bool(encoding_settings[3])
                self.resize_width = encoding_settings[4]
                self.resize_height = encoding_settings[5]
                self.video_bitrate = encoding_settings[6]
                self.audio_bitrate = encoding_settings[7]
                self.encoding_speed = encoding_settings[8]
                self.deinterlace = to_bool(encoding_settings[9])
                self.command_line = encoding_settings[10]
        super(EditConvertVideo, self).__init__(**kwargs)

    def refresh_buttons(self):
        pass

    def save_last(self):
        pass

    def load_last(self):
        pass

    def store_settings(self):
        encoding_preset = self.file_format+','+self.video_codec+','+self.audio_codec+','+str(self.resize)+','+self.resize_width+','+self.resize_height+','+self.video_bitrate+','+self.audio_bitrate+','+self.encoding_speed+','+str(self.deinterlace)+','+self.command_line
        app = App.get_running_app()
        app.config.set('Presets', 'encoding', encoding_preset)

    def setup_dropdowns(self):
        """Creates and populates the various drop-down menus used by this dialog."""

        self.preset_drop = NormalDropDown()
        app = App.get_running_app()
        for index, preset in enumerate(app.encoding_presets):
            menu_button = MenuButton(text=preset['name'])
            menu_button.bind(on_release=self.set_preset)
            self.preset_drop.add_widget(menu_button)

        self.file_format = containers_friendly[0]
        self.container_drop = NormalDropDown()
        for container in containers_friendly:
            menu_button = MenuButton(text=container)
            menu_button.bind(on_release=self.change_container_to)
            self.container_drop.add_widget(menu_button)

        self.video_codec = video_codecs_friendly[0]
        self.video_codec_drop = NormalDropDown()
        for codec in video_codecs_friendly:
            menu_button = MenuButton(text=codec)
            menu_button.bind(on_release=self.change_video_codec_to)
            self.video_codec_drop.add_widget(menu_button)

        #self.video_quality = 'Constant Bitrate'
        #video_qualities = ['Constant Bitrate', 'High', 'Medium', 'Low', 'Very Low']
        #self.video_quality_drop = NormalDropDown()
        #for quality in video_qualities:
        #    menu_button = MenuButton(text=quality)
        #    menu_button.bind(on_release=self.change_video_quality_to)
        #    self.video_quality_drop.add_widget(menu_button)

        self.encoding_speed = 'Fast'
        encoding_speeds = ['Very Fast', 'Fast', 'Medium', 'Slow', 'Very Slow']
        self.encoding_speed_drop = NormalDropDown()
        for speed in encoding_speeds:
            menu_button = MenuButton(text=speed)
            menu_button.bind(on_release=self.change_encoding_speed_to)
            self.encoding_speed_drop.add_widget(menu_button)

        self.audio_codec = audio_codecs_friendly[0]
        self.audio_codec_drop = NormalDropDown()
        for codec in audio_codecs_friendly:
            menu_button = MenuButton(text=codec)
            menu_button.bind(on_release=self.change_audio_codec_to)
            self.audio_codec_drop.add_widget(menu_button)

    def update_deinterlace(self, state):
        if state == 'down':
            self.deinterlace = True
        else:
            self.deinterlace = False

    def update_resize(self, state):
        if state == 'down':
            self.resize = True
        else:
            self.resize = False

    def set_resize_width(self, instance):
        self.resize_width = instance.text
        self.store_settings()

    def set_resize_height(self, instance):
        self.resize_height = instance.text
        self.store_settings()

    def set_preset(self, instance):
        """Sets the current dialog preset settings to one of the presets stored in the app.
        Argument:
            index: Integer, the index of the preset to set.
        """

        self.preset_drop.dismiss()
        app = App.get_running_app()
        for preset in app.encoding_presets:
            if preset['name'] == instance.text:
                if preset['file_format'] in containers_friendly:
                    self.file_format = preset['file_format']
                else:
                    self.file_format = containers_friendly[0]
                if preset['video_codec'] in video_codecs_friendly:
                    self.video_codec = preset['video_codec']
                else:
                    self.video_codec = video_codecs_friendly[0]
                if preset['audio_codec'] in audio_codecs_friendly:
                    self.audio_codec = preset['audio_codec']
                else:
                    self.audio_codec = audio_codecs_friendly[0]
                self.resize = preset['resize']
                self.resize_width = preset['width']
                self.resize_height = preset['height']
                self.video_bitrate = preset['video_bitrate']
                self.audio_bitrate = preset['audio_bitrate']
                self.encoding_speed = preset['encoding_speed']
                self.deinterlace = preset['deinterlace']
                self.command_line = preset['command_line']
                self.store_settings()
                return

    def on_video_bitrate(self, *_):
        self.store_settings()

    def on_audio_bitrate(self, *_):
        self.store_settings()

    def set_command_line(self, instance):
        self.command_line = instance.text
        self.store_settings()

    def change_video_quality_to(self, instance):
        """Sets the self.video_quality value."""

        self.video_quality_drop.dismiss()
        self.video_quality = instance.text
        self.store_settings()

    def change_encoding_speed_to(self, instance):
        """Sets the self.encoding_speed value."""

        self.encoding_speed_drop.dismiss()
        self.encoding_speed = instance.text
        self.store_settings()

    def change_audio_codec_to(self, instance):
        """Sets the self.audio_codec value."""

        self.audio_codec_drop.dismiss()
        self.audio_codec = instance.text
        self.store_settings()

    def change_video_codec_to(self, instance):
        """Sets the self.video_codec value."""

        self.video_codec_drop.dismiss()
        self.video_codec = instance.text
        self.store_settings()

    def change_container_to(self, instance):
        """Sets the self.file_format value."""

        self.container_drop.dismiss()
        self.file_format = instance.text
        self.store_settings()

    def encode(self):
        """Pass encoding settings to owner album screen and tell it to begin encoding process."""

        #file_format = containers[containers_friendly.index(self.file_format)]
        #video_codec = video_codecs[video_codecs_friendly.index(self.video_codec)]
        #audio_codec = audio_codecs[audio_codecs_friendly.index(self.audio_codec)]
        encoding_settings = {'file_format': self.file_format,
                             'video_codec': self.video_codec,
                             'audio_codec': self.audio_codec,
                             'resize': self.resize,
                             'width': self.resize_width,
                             'height': self.resize_height,
                             'video_bitrate': self.video_bitrate,
                             'audio_bitrate': self.audio_bitrate,
                             'encoding_speed': self.encoding_speed,
                             'deinterlace': self.deinterlace,
                             'command_line': self.command_line}
        self.owner.encoding_settings = encoding_settings
        print(encoding_settings)
        self.store_settings()
        self.owner.begin_encode()