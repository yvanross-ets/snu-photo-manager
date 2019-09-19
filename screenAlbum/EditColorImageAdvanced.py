from io import BytesIO

from PIL import Image, ImageDraw, ImageChops
from kivy.app import App
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.uix.gridlayout import GridLayout

from screenAlbum import VideoEncodePreset

from kivy.lang.builder import Builder

Builder.load_string("""
<EditColorImageAdvanced>:
    padding: 0, 0, int(app.button_scale / 2), 0
    id: editColor
    size_hint: 1, None
    cols: 1
    height: self.minimum_height
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        WideButton:
            text: 'Confirm Edit'
            on_release: root.owner.save_edit()
        WideButton:
            text: 'Cancel Edit'
            warn: True
            on_release: root.owner.set_edit_panel('main')
    WideButton:
        id: loadLast
        disabled: not root.owner.edit_advanced
        text: "Load Last Settings"
        on_release: root.load_last()
    MediumBufferY:
    GridLayout:
        id: videoPreset
        cols: 1
        height: self.minimum_height
        size_hint_y: None
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        LeftNormalLabel:
            text: 'Color Adjustments:'
        NormalButton:
            text: 'Reset All'
            on_release: root.r/eset_all()
    BoxLayout:
        canvas.before:
            Color:
                rgba:0,0,0,1
            Rectangle:
                size: self.size
                pos: self.pos
        size_hint_y: None
        height: self.width * .5
        Image:
            id: histogram
            allow_stretch: True
            keep_ratio: False
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
                text: 'Curves:'
            NormalButton:
                text: 'Remove Point'
                on_release: root.remove_point()
            NormalButton:
                text: 'Reset'
                on_release: root.reset_curves()
        BoxLayout:
            size_hint_y: None
            height: self.width * .66
            Curves:
                id: curves
        #BoxLayout:
        #    orientation: 'horizontal'
        #    size_hint_y: None
        #    height: app.button_scale
        #    LeftNormalLabel:
        #        text: 'Interpolation Mode:'
        #    MenuStarterButton:
        #        size_hint_x: 1
        #        id: interpolation
        #        text: app.interpolation
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
                text: 'Tinting:'
            NormalButton:
                text: 'Reset'
                on_release: root.reset_tint()
        BoxLayout:
            size_hint_y: None
            height: sp(33)*10
            ColorPickerCustom:
                id: tint
                color: root.tint
                on_color: root.tint = self.color
""")

class EditColorImageAdvanced(GridLayout):
    """Panel to expose advanced color editing options."""

    tint = ListProperty([1.0, 1.0, 1.0, 1.0])
    curve = ListProperty([[0, 0], [1, 1]])

    owner = ObjectProperty()
    interpolation_drop_down = ObjectProperty()
    preset_name = StringProperty()

    def __init__(self, **kwargs):
        Clock.schedule_once(self.add_video_preset)
        super(EditColorImageAdvanced, self).__init__(**kwargs)
        #self.interpolation_drop_down = InterpolationDropDown()
        #interpolation_button = self.ids['interpolation']
        #interpolation_button.bind(on_release=self.interpolation_drop_down.open)
        #self.interpolation_drop_down.bind(on_select=self.set_interpolation)

    def refresh_buttons(self):
        pass

    def add_video_preset(self, *_):
        if not self.owner.view_image:
            video_preset = self.ids['videoPreset']
            video_preset.add_widget(VideoEncodePreset())

    def save_last(self):
        self.owner.edit_advanced = True
        self.owner.tint = self.tint
        curves = self.ids['curves']
        self.curve = curves.points
        self.owner.curve = self.curve

    def load_last(self):
        self.tint = self.owner.tint
        self.curve = self.owner.curve
        curves = self.ids['curves']
        curves.points = self.curve
        curves.refresh()

    def set_interpolation(self, instance, value):
        """Sets the interpolation mode.
        Arguments:
            instance: Widget that called this function.  Not used.
            value: String, new value to set interpolation to.
        """

        del instance
        app = App.get_running_app()
        app.interpolation = value
        curves = self.ids['curves']
        curves.refresh()

    def draw_histogram(self, *_):
        """Draws the histogram image and displays it."""

        histogram_data = self.owner.viewer.edit_image.histogram
        histogram = self.ids['histogram']
        histogram_max = max(histogram_data)
        data_red = histogram_data[0:256]
        data_green = histogram_data[256:512]
        data_blue = histogram_data[512:768]
        multiplier = 256.0/histogram_max

        #Draw red channel
        histogram_red = Image.new(mode='RGB', size=(256, 256), color=(0, 0, 0))
        draw = ImageDraw.Draw(histogram_red)
        for index in range(256):
            value = int(data_red[index]*multiplier)
            draw.line((index, 256, index, 256-value), fill=(255, 0, 0))

        #Draw green channel
        histogram_green = Image.new(mode='RGB', size=(256, 256), color=(0, 0, 0))
        draw = ImageDraw.Draw(histogram_green)
        for index in range(256):
            value = int(data_green[index]*multiplier)
            draw.line((index, 256, index, 256-value), fill=(0, 255, 0))

        #Draw blue channel
        histogram_blue = Image.new(mode='RGB', size=(256, 256), color=(0, 0, 0))
        draw = ImageDraw.Draw(histogram_blue)
        for index in range(256):
            value = int(data_blue[index]*multiplier)
            draw.line((index, 256, index, 256-value), fill=(0, 0, 255))

        #Mix channels together
        histogram_red_green = ImageChops.add(histogram_red, histogram_green)
        histogram_image = ImageChops.add(histogram_red_green, histogram_blue)

        #Convert and display image
        image_bytes = BytesIO()
        histogram_image.save(image_bytes, 'jpeg')
        image_bytes.seek(0)
        histogram._coreimage = CoreImage(image_bytes, ext='jpg')
        histogram._on_tex_change()

    def reset_curves(self):
        """Tells the curves widget to reset to its default points."""

        curves = self.ids['curves']
        curves.reset()

    def remove_point(self):
        """Tells the curves widget to remove its last point."""

        curves = self.ids['curves']
        curves.remove_point()

    def on_tint(self, *_):
        self.owner.viewer.edit_image.tint = self.tint

    def reset_tint(self):
        self.tint = [1.0, 1.0, 1.0, 1.0]

    def reset_all(self):
        """Reset all edit settings on this panel."""

        self.reset_curves()
        self.reset_tint()