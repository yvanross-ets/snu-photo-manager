from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.gridlayout import GridLayout

from kivy.lang.builder import Builder

Builder.load_string("""
<EditRotateImage>:
    padding: 0, 0, int(app.button_scale / 2), 0
    cols: 1
    size_hint_y: None
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
    MediumBufferY:
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        LeftNormalLabel:
            text: 'Image Rotation:'
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
        GridLayout:
            cols: 4
            size_hint_y: None
            size_hint_x: 1
            height: app.button_scale
            NormalToggle:
                id: angles_0
                size_hint_x: 1
                state: 'down'
                text: '0'
                group: 'angles'
                on_press: root.update_angle(0)
            NormalToggle:
                id: angles_90
                size_hint_x: 1
                text: '90'
                group: 'angles'
                on_press: root.update_angle(90)
            NormalToggle:
                id: angles_180
                size_hint_x: 1
                text: '180'
                group: 'angles'
                on_press: root.update_angle(180)
            NormalToggle:
                id: angles_270
                size_hint_x: 1
                text: '270'
                group: 'angles'
                on_press: root.update_angle(270)
        GridLayout:
            cols: 2
            size_hint: 1, None
            height: app.button_scale
            orientation: 'horizontal'
            NormalToggle:
                text_size: self.size
                halign: 'center'
                valign: 'middle'
                id: flip_horizontal
                size_hint_x: 1
                text: 'Horizontal Flip'
                on_press: root.update_flip_horizontal(self.state)
            NormalToggle:
                text_size: self.size
                halign: 'center'
                valign: 'middle'
                id: flip_vertical
                size_hint_x: 1
                text: 'Vertical Flip'
                on_press: root.update_flip_vertical(self.state)

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
        NormalLabel:
            text: 'Fine Rotation:'
        NormalSlider:
            id: fine_angle
            value: root.fine_angle
            on_value: root.fine_angle = self.value

""")



class EditRotateImage(GridLayout):
    """Panel to expose rotation editing options."""

    fine_angle = NumericProperty(0)
    owner = ObjectProperty()

    def refresh_buttons(self):
        pass

    def save_image(self, *_):
        if self.owner.viewer.edit_image.video:
            self.owner.save_video()
        else:
            self.owner.save_image()

    def save_last(self):
        pass

    def load_last(self):
        pass

    def reset_all(self):
        self.update_angle(0)
        self.ids['angles_0'].state = 'down'
        self.ids['angles_90'].state = 'normal'
        self.ids['angles_180'].state = 'normal'
        self.ids['angles_270'].state = 'normal'
        self.fine_angle = 0
        self.ids['fine_angle'].value = 0
        self.update_flip_horizontal(flip='up')
        self.ids['flip_horizontal'].state = 'normal'
        self.update_flip_vertical(flip='up')
        self.ids['flip_vertical'].state = 'normal'

    def update_angle(self, angle):
        self.owner.viewer.edit_image.rotate_angle = angle

    def on_fine_angle(self, *_):
        self.owner.viewer.edit_image.fine_angle = self.fine_angle

    def update_flip_horizontal(self, flip):
        if flip == 'down':
            self.owner.viewer.edit_image.flip_horizontal = True
        else:
            self.owner.viewer.edit_image.flip_horizontal = False

    def update_flip_vertical(self, flip):
        if flip == 'down':
            self.owner.viewer.edit_image.flip_vertical = True
        else:
            self.owner.viewer.edit_image.flip_vertical = False