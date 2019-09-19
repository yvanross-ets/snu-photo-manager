from io import BytesIO

from PIL import Image, ImageDraw, ImageChops
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.gridlayout import GridLayout

from screenAlbum import VideoEncodePreset

from kivy.lang.builder import Builder

Builder.load_string("""
<EditColorImage>:
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
        disabled: not root.owner.edit_color
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
            on_release: root.reset_all()
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
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        NormalToggle:
            text: "Auto Contrast"
            id: autocontrastToggle
            state: 'down' if root.autocontrast else 'normal'
            on_state: root.update_autocontrast(self.state)
            size_hint_x: 1
    SmallBufferY:
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        LeftNormalLabel:
            text: 'Equalize Histogram:'
        NormalButton:
            text: 'Reset'
            on_release: root.reset_equalize()
    HalfSlider:
        id: equalizeSlider
        value: root.equalize
        on_value: root.equalize = self.value
    SmallBufferY:
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale if root.owner.opencv else 0
        disabled: not root.owner.opencv
        opacity: 1 if root.owner.opencv else 0
        LeftNormalLabel:
            text: 'Adaptive Histogram Equalize:'
        NormalButton:
            text: 'Reset'
            on_release: root.reset_adaptive()
    HalfSlider:
        disabled: not root.owner.opencv
        opacity: 1 if root.owner.opencv else 0
        height: app.button_scale if root.owner.opencv else 0
        id: adaptiveSlider
        value: root.adaptive
        on_value: root.adaptive = self.value
    SmallBufferY:
        height: int(app.button_scale / 4) if root.owner.opencv else 0
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        LeftNormalLabel:
            text: 'Highs:'
        NormalButton:
            text: 'Reset'
            on_release: root.reset_brightness()
    NormalSlider:
        id: brightnessSlider
        value: root.brightness
        on_value: root.brightness = self.value
    SmallBufferY:
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        LeftNormalLabel:
            text: 'Mids:'
        NormalButton:
            text: 'Reset'
            on_release: root.reset_gamma()
    NormalSlider:
        id: gammaSlider
        value: root.gamma
        on_value: root.gamma = self.value
    SmallBufferY:
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        LeftNormalLabel:
            text: 'Lows:'
        NormalButton:
            text: 'Reset'
            on_release: root.reset_shadow()
    NormalSlider:
        id: shadowSlider
        value: root.shadow
        on_value: root.shadow = self.value
    SmallBufferY:
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        LeftNormalLabel:
            text: 'Saturation:'
        NormalButton:
            text: 'Reset'
            on_release: root.reset_saturation()
    NormalSlider:
        id: saturationSlider
        value: root.saturation
        on_value: root.saturation = self.value
    SmallBufferY:
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        LeftNormalLabel:
            text: 'Color Temperature:'
        NormalButton:
            text: 'Reset'
            on_release: root.reset_temperature()
    NormalSlider:
        id: temperatureSlider
        value: root.temperature
        on_value: root.temperature = self.value
""")

class EditColorImage(GridLayout):
    """Panel to expose color editing options."""

    equalize = NumericProperty(0)
    autocontrast = BooleanProperty(False)
    adaptive = NumericProperty(0)
    brightness = NumericProperty(0)
    shadow = NumericProperty(0)
    gamma = NumericProperty(0)
    contrast = NumericProperty(0)
    saturation = NumericProperty(0)
    temperature = NumericProperty(0)

    owner = ObjectProperty()
    interpolation_drop_down = ObjectProperty()
    preset_name = StringProperty()

    def __init__(self, **kwargs):
        Clock.schedule_once(self.add_video_preset)
        super(EditColorImage, self).__init__(**kwargs)

    def refresh_buttons(self):
        pass

    def add_video_preset(self, *_):
        if not self.owner.view_image:
            video_preset = self.ids['videoPreset']
            video_preset.add_widget(VideoEncodePreset())

    def save_last(self):
        self.owner.edit_color = True
        self.owner.equalize = self.equalize
        self.owner.autocontrast = self.autocontrast
        self.owner.adaptive = self.adaptive
        self.owner.brightness = self.brightness
        self.owner.gamma = self.gamma
        self.owner.contrast = self.contrast
        self.owner.saturation = self.saturation
        self.owner.temperature = self.temperature
        self.owner.shadow = self.shadow

    def load_last(self):
        self.equalize = self.owner.equalize
        self.autocontrast = self.owner.autocontrast
        self.adaptive = self.owner.adaptive
        self.brightness = self.owner.brightness
        self.gamma = self.owner.gamma
        self.contrast = self.owner.contrast
        self.saturation = self.owner.saturation
        self.temperature = self.owner.temperature
        self.shadow = self.owner.shadow

    def draw_histogram(self, *_):
        """Draws the histogram image and displays it."""

        size = 256  #Determines histogram resolution
        size_multiplier = int(256/size)
        histogram_data = self.owner.viewer.edit_image.histogram
        if len(histogram_data) == 768:
            histogram = self.ids['histogram']
            histogram_max = max(histogram_data)
            data_red = histogram_data[0:256]
            data_green = histogram_data[256:512]
            data_blue = histogram_data[512:768]
            multiplier = 256.0/histogram_max/size_multiplier

            #Draw red channel
            histogram_red = Image.new(mode='RGB', size=(size, size), color=(0, 0, 0))
            draw = ImageDraw.Draw(histogram_red)
            for index in range(size):
                value = int(data_red[index*size_multiplier]*multiplier)
                draw.line((index, size, index, size-value), fill=(255, 0, 0))

            #Draw green channel
            histogram_green = Image.new(mode='RGB', size=(size, size), color=(0, 0, 0))
            draw = ImageDraw.Draw(histogram_green)
            for index in range(size):
                value = int(data_green[index*size_multiplier]*multiplier)
                draw.line((index, size, index, size-value), fill=(0, 255, 0))

            #Draw blue channel
            histogram_blue = Image.new(mode='RGB', size=(size, size), color=(0, 0, 0))
            draw = ImageDraw.Draw(histogram_blue)
            for index in range(size):
                value = int(data_blue[index*size_multiplier]*multiplier)
                draw.line((index, size, index, size-value), fill=(0, 0, 255))

            #Mix channels together
            histogram_red_green = ImageChops.add(histogram_red, histogram_green)
            histogram_image = ImageChops.add(histogram_red_green, histogram_blue)

            #Convert and display image
            image_bytes = BytesIO()
            histogram_image.save(image_bytes, 'jpeg')
            image_bytes.seek(0)
            histogram._coreimage = CoreImage(image_bytes, ext='jpg')
            histogram._on_tex_change()

    def on_equalize(self, *_):
        self.owner.viewer.edit_image.equalize = self.equalize

    def update_equalize(self, value):
        if value == 'down':
            self.equalize = True
        else:
            self.equalize = False
        self.draw_histogram()

    def reset_equalize(self):
        self.equalize = 0

    def on_autocontrast(self, *_):
        self.owner.viewer.edit_image.autocontrast = self.autocontrast

    def update_autocontrast(self, value):
        if value == 'down':
            self.autocontrast = True
        else:
            self.autocontrast = False

    def reset_autocontrast(self):
        self.autocontrast = False

    def on_adaptive(self, *_):
        self.owner.viewer.edit_image.adaptive_clip = self.adaptive

    def reset_adaptive(self):
        self.adaptive = 0

    def on_brightness(self, *_):
        self.owner.viewer.edit_image.brightness = self.brightness

    def reset_brightness(self):
        self.brightness = 0

    def on_shadow(self, *_):
        self.owner.viewer.edit_image.shadow = self.shadow

    def reset_shadow(self):
        self.shadow = 0

    def on_gamma(self, *_):
        self.owner.viewer.edit_image.gamma = self.gamma

    def reset_gamma(self):
        self.gamma = 0

    def on_contrast(self, *_):
        self.owner.viewer.edit_image.contrast = self.contrast

    def reset_contrast(self):
        self.contrast = 0

    def on_saturation(self, *_):
        self.owner.viewer.edit_image.saturation = self.saturation

    def reset_saturation(self):
        self.saturation = 0

    def on_temperature(self, *_):
        self.owner.viewer.edit_image.temperature = self.temperature

    def reset_temperature(self):
        self.temperature = 0

    def reset_all(self):
        """Reset all edit settings on this panel."""

        self.reset_brightness()
        self.reset_shadow()
        self.reset_gamma()
        self.reset_contrast()
        self.reset_saturation()
        self.reset_temperature()
        self.reset_equalize()
        self.reset_autocontrast()
        self.reset_adaptive()