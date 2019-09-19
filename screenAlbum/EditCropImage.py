from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.gridlayout import GridLayout

from screenAlbum.AspectRatioDropdown import AspectRatioDropDown
from kivy.lang.builder import Builder

Builder.load_string("""
<EditCropImage>:
    padding: 0, 0, int(app.button_scale / 2), 0
    cols: 1
    height: self.minimum_height
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        WideButton:
            text: 'Confirm Edit'
            on_release: root.save_image()
        WideButton:
            text: 'Cancel Edit'
            warn: True
            on_release: root.owner.set_edit_panel('main')
    WideButton:
        id: loadLast
        disabled: not root.owner.edit_crop
        text: "Load Last Settings"
        on_release: root.load_last()
    MediumBufferY:
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        LeftNormalLabel:
            text: 'Image Cropping:'
        NormalButton:
            text: 'Reset All'
            on_release: root.reset_crop()
    LeftNormalLabel:
        size_hint_y: None
        height: app.button_scale
        text: root.crop_size
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
                text: 'Crop Top:'
            ShortLabel:
                text: str(round(cropTopSlider.value * 100, 1))+'%'
        HalfSlider:
            id: cropTopSlider
            value: root.crop_top
            on_value: root.crop_top = self.value
        SmallBufferY:
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            LeftNormalLabel:
                text: 'Crop Right:'
            ShortLabel:
                text: str(round(cropRightSlider.value * 100, 1))+'%'
        HalfSlider:
            id: cropRightSlider
            value: root.crop_right
            on_value: root.crop_right = self.value
        SmallBufferY:
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            LeftNormalLabel:
                text: 'Crop Bottom:'
            ShortLabel:
                text: str(round(cropBottomSlider.value * 100, 1))+'%'
        HalfSlider:
            id: cropBottomSlider
            value: root.crop_bottom
            on_value: root.crop_bottom = self.value
        SmallBufferY:
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            LeftNormalLabel:
                text: 'Crop Left:'
            ShortLabel:
                text: str(round(cropLeftSlider.value * 100, 1))+'%'
        HalfSlider:
            id: cropLeftSlider
            value: root.crop_left
            on_value: root.crop_left = self.value
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
        MenuStarterButtonWide:
            size_hint_x: 1
            text: 'Set Aspect Ratio...'
            id: aspectRatios
            on_release: root.aspect_dropdown.open(self)
        GridLayout:
            cols: 2
            size_hint: 1, None
            height: app.button_scale
            NormalToggle:
                id: horizontalToggle
                size_hint_x: 1
                text: 'Horizontal'
                state: 'down' if root.orientation == 'horizontal' else 'normal'
                group: 'orientation'
                on_press: root.set_orientation('horizontal')
            NormalToggle:
                id: verticalToggle
                size_hint_x: 1
                text: 'Vertical'
                state: 'down' if root.orientation == 'vertical' else 'normal'
                group: 'orientation'
                on_press: root.set_orientation('vertical')
""")

class EditCropImage(GridLayout):
    """Panel to expose crop editing options."""

    crop_top = NumericProperty(0)
    crop_right = NumericProperty(0)
    crop_bottom = NumericProperty(0)
    crop_left = NumericProperty(0)

    owner = ObjectProperty()
    image_x = NumericProperty(0)
    image_y = NumericProperty(0)
    orientation = StringProperty('horizontal')
    aspect_x = NumericProperty(0)
    aspect_y = NumericProperty(0)
    crop_size = StringProperty('')

    def __init__(self, **kwargs):
        super(EditCropImage, self).__init__(**kwargs)
        self.aspect_dropdown = AspectRatioDropDown()
        self.aspect_dropdown.bind(on_select=lambda instance, x: self.set_aspect_ratio(x))
        self.aspect_x = self.image_x
        self.aspect_y = self.image_y
        if self.image_x >= self.image_y:
            self.orientation = 'horizontal'
            self.ids['horizontalToggle'].state = 'down'
        else:
            self.orientation = 'vertical'
            self.ids['verticalToggle'].state = 'down'

    def refresh_buttons(self):
        pass

    def save_image(self, *_):
        if self.owner.viewer.edit_image.video:
            self.owner.save_video()
        else:
            self.owner.save_image()

    def update_crop_size_text(self):
        edit_image = self.owner.viewer.edit_image
        if edit_image:
            edit_image.get_crop_size()

    def update_crop(self):
        edit_image = self.owner.viewer.edit_image
        if edit_image:
            percents = edit_image.get_crop_percent()
            self.crop_top = percents[0]
            self.crop_right = percents[1]
            self.crop_bottom = percents[2]
            self.crop_left = percents[3]

    def save_last(self):
        self.update_crop()
        self.owner.edit_crop = True
        self.owner.crop_top = self.crop_top
        self.owner.crop_right = self.crop_right
        self.owner.crop_bottom = self.crop_bottom
        self.owner.crop_left = self.crop_left

    def load_last(self):
        self.crop_top = self.owner.crop_top
        self.crop_right = self.owner.crop_right
        self.crop_bottom = self.owner.crop_bottom
        self.crop_left = self.owner.crop_left

    def on_crop_top(self, *_):
        edit_image = self.owner.viewer.edit_image
        if edit_image:
            edit_image.crop_percent('top', self.crop_top)
            self.update_crop_size_text()

    def on_crop_right(self, *_):
        edit_image = self.owner.viewer.edit_image
        if edit_image:
            edit_image.crop_percent('right', self.crop_right)
            self.update_crop_size_text()

    def on_crop_bottom(self, *_):
        edit_image = self.owner.viewer.edit_image
        if edit_image:
            edit_image.crop_percent('bottom', self.crop_bottom)
            self.update_crop_size_text()

    def on_crop_left(self, *_):
        edit_image = self.owner.viewer.edit_image
        if edit_image:
            edit_image.crop_percent('left', self.crop_left)
            self.update_crop_size_text()

    def recrop(self):
        """tell image to recrop itself based on an aspect ratio"""

        edit_image = self.owner.viewer.edit_image
        if edit_image:
            edit_image.set_aspect(self.aspect_x, self.aspect_y)
            self.update_crop()

    def reset_crop(self):
        edit_image = self.owner.viewer.edit_image
        if edit_image:
            edit_image.reset_crop()
            self.update_crop()

    def set_orientation(self, orientation):
        if orientation != self.orientation:
            old_x = self.aspect_x
            old_y = self.aspect_y
            self.aspect_x = old_y
            self.aspect_y = old_x
        self.orientation = orientation

    def set_aspect_ratio(self, method):
        if method == '6x4':
            if self.orientation == 'horizontal':
                self.aspect_x = 6
                self.aspect_y = 4
            else:
                self.aspect_x = 4
                self.aspect_y = 6
        elif method == '7x5':
            if self.orientation == 'horizontal':
                self.aspect_x = 7
                self.aspect_y = 5
            else:
                self.aspect_x = 5
                self.aspect_y = 7
        elif method == '11x8.5':
            if self.orientation == 'horizontal':
                self.aspect_x = 11
                self.aspect_y = 8.5
            else:
                self.aspect_x = 8.5
                self.aspect_y = 11
        elif method == '4x3':
            if self.orientation == 'horizontal':
                self.aspect_x = 4
                self.aspect_y = 3
            else:
                self.aspect_x = 3
                self.aspect_y = 4
        elif method == '16x9':
            if self.orientation == 'horizontal':
                self.aspect_x = 16
                self.aspect_y = 9
            else:
                self.aspect_x = 9
                self.aspect_y = 16
        elif method == '1x1':
            self.aspect_x = 1
            self.aspect_y = 1
        else:
            if self.image_x >= self.image_y:
                width = self.image_x
                height = self.image_y
            else:
                width = self.image_y
                height = self.image_x
            if self.orientation == 'horizontal':
                self.aspect_x = width
                self.aspect_y = height
            else:
                self.aspect_x = height
                self.aspect_y = width
        self.recrop()