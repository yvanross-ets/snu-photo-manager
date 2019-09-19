from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.gridlayout import GridLayout

from screenAlbum import VideoEncodePreset
from kivy.lang.builder import Builder

Builder.load_string("""
<EditFilterImage>:
    padding: 0, 0, int(app.button_scale / 2), 0
    cols: 1
    size_hint: 1, None
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
        disabled: not root.owner.edit_filter
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
            text: 'Filter Image:'
        NormalButton:
            text: 'Reset All'
            on_release: root.reset_all()
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
                text: 'Soften/Sharpen:'
            NormalButton:
                text: 'Reset'
                on_release: root.reset_sharpen()
        NormalSlider:
            id: sharpenSlider
            value: root.sharpen
            on_value: root.sharpen = self.value
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale if root.owner.opencv else 0
            opacity: 1 if root.owner.opencv else 0
            LeftNormalLabel:
                text: 'Median Blur (Despeckle):'
            NormalButton:
                text: 'Reset'
                on_release: root.reset_median()
                disabled: not root.owner.opencv
        HalfSlider:
            height: app.button_scale if root.owner.opencv else 0
            opacity: 1 if root.owner.opencv else 0
            id: medianSlider
            value: root.median
            on_value: root.median = self.value
            disabled: not root.owner.opencv
    MediumBufferY:
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
        height: self.minimum_height if root.owner.opencv else 0
        disabled: not root.owner.opencv
        opacity: 1 if root.owner.opencv else 0
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            LeftNormalLabel:
                text: 'Edge-Preserve Blur:'
            NormalButton:
                text: 'Reset'
                on_release: root.reset_bilateral_amount()
        HalfSlider:
            id: bilateralAmountSlider
            value: root.bilateral_amount
            on_value: root.bilateral_amount = self.value
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            LeftNormalLabel:
                text: 'Blur Size:'
            NormalButton:
                text: 'Reset'
                on_release: root.reset_bilateral()
        HalfSlider:
            id: bilateralSlider
            value: root.bilateral
            on_value: root.bilateral = self.value
    MediumBufferY:
        height: int(app.button_scale / 2) if root.owner.opencv else 0
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
                text: 'Vignette:'
            NormalButton:
                text: 'Reset'
                on_release: root.reset_vignette_amount()
        HalfSlider:
            id: vignetteAmountSlider
            value: root.vignette_amount
            on_value: root.vignette_amount = self.value
        SmallBufferY:
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            LeftNormalLabel:
                text: 'Size:'
            NormalButton:
                text: 'Reset'
                on_release: root.reset_vignette_size()
        HalfSlider:
            value: .5
            id: vignetteSizeSlider
            value: root.vignette_size
            on_value: root.vignette_size = self.value
    MediumBufferY:
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
                text: 'Edge Blur:'
            NormalButton:
                text: 'Reset'
                on_release: root.reset_edge_blur_amount()
        HalfSlider:
            id: edgeBlurAmountSlider
            value: root.edge_blur_amount
            on_value: root.edge_blur_amount = self.value
        SmallBufferY:
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            LeftNormalLabel:
                text: 'Size:'
            NormalButton:
                text: 'Reset'
                on_release: root.reset_edge_blur_size()
        HalfSlider:
            value: .5
            id: edgeBlurSizeSlider
            value: root.edge_blur_size
            on_value: root.edge_blur_size = self.value
        SmallBufferY:
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            LeftNormalLabel:
                text: 'Intensity:'
            NormalButton:
                text: 'Reset'
                on_release: root.reset_edge_blur_intensity()
        HalfSlider:
            value: .5
            id: edgeBlurIntensitySlider
            value: root.edge_blur_intensity
            on_value: root.edge_blur_intensity = self.value
""")

class EditFilterImage(GridLayout):
    """Panel to expose filter editing options."""

    sharpen = NumericProperty(0)
    vignette_amount = NumericProperty(0)
    vignette_size = NumericProperty(0.5)
    edge_blur_amount = NumericProperty(0)
    edge_blur_size = NumericProperty(0.5)
    edge_blur_intensity = NumericProperty(0.5)
    median = NumericProperty(0)
    bilateral = NumericProperty(0.5)
    bilateral_amount = NumericProperty(0)

    owner = ObjectProperty()
    preset_name = StringProperty()

    def __init__(self, **kwargs):
        Clock.schedule_once(self.add_video_preset)
        super(EditFilterImage, self).__init__(**kwargs)

    def refresh_buttons(self):
        pass

    def add_video_preset(self, *_):
        if not self.owner.view_image:
            video_preset = self.ids['videoPreset']
            video_preset.add_widget(VideoEncodePreset())

    def save_last(self):
        self.owner.edit_filter = True
        self.owner.sharpen = self.sharpen
        self.owner.vignette_amount = self.vignette_amount
        self.owner.vignette_size = self.vignette_size
        self.owner.edge_blur_amount = self.edge_blur_amount
        self.owner.edge_blur_size = self.edge_blur_size
        self.owner.edge_blur_intensity = self.edge_blur_intensity
        self.owner.bilateral = self.bilateral
        self.owner.bilateral_amount = self.bilateral_amount
        self.owner.median = self.median

    def load_last(self):
        self.sharpen = self.owner.sharpen
        self.vignette_amount = self.owner.vignette_amount
        self.vignette_size = self.owner.vignette_size
        self.edge_blur_amount = self.owner.edge_blur_amount
        self.edge_blur_size = self.owner.edge_blur_size
        self.edge_blur_intensity = self.owner.edge_blur_intensity
        self.bilateral = self.owner.bilateral
        self.bilateral_amount = self.owner.bilateral_amount
        self.median = self.owner.median

    def on_sharpen(self, *_):
        self.owner.viewer.edit_image.sharpen = self.sharpen

    def reset_sharpen(self):
        self.sharpen = 0

    def on_median(self, *_):
        self.owner.viewer.edit_image.median_blur = self.median

    def reset_median(self):
        self.median = 0

    def on_bilateral_amount(self, *_):
        self.owner.viewer.edit_image.bilateral_amount = self.bilateral_amount

    def reset_bilateral_amount(self):
        self.bilateral_amount = 0

    def on_bilateral(self, *_):
        self.owner.viewer.edit_image.bilateral = self.bilateral

    def reset_bilateral(self):
        self.bilateral = 0.5

    def on_vignette_amount(self, *_):
        self.owner.viewer.edit_image.vignette_amount = self.vignette_amount

    def reset_vignette_amount(self):
        self.vignette_amount = 0

    def on_vignette_size(self, *_):
        self.owner.viewer.edit_image.vignette_size = self.vignette_size

    def reset_vignette_size(self):
        self.vignette_size = 0.5

    def on_edge_blur_amount(self, *_):
        self.owner.viewer.edit_image.edge_blur_amount = self.edge_blur_amount

    def reset_edge_blur_amount(self):
        self.edge_blur_amount = 0

    def on_edge_blur_size(self, *_):
        self.owner.viewer.edit_image.edge_blur_size = self.edge_blur_size

    def reset_edge_blur_size(self):
        self.edge_blur_size = 0.5

    def on_edge_blur_intensity(self, *_):
        self.owner.viewer.edit_image.edge_blur_intensity = self.edge_blur_intensity

    def reset_edge_blur_intensity(self):
        self.edge_blur_intensity = 0.5

    def reset_all(self):
        """Reset all edit values to defaults."""

        self.reset_sharpen()
        self.reset_vignette_amount()
        self.reset_vignette_size()
        self.reset_edge_blur_amount()
        self.reset_edge_blur_size()
        self.reset_edge_blur_intensity()
        self.reset_median()
        self.reset_bilateral()
        self.reset_bilateral_amount()