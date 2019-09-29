import os

from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, ListProperty, ObjectProperty
from kivy.uix.gridlayout import GridLayout

from generalElements.treeviews.TreeViewButton import TreeViewButton
from screenAlbum import VideoEncodePreset

from kivy.lang.builder import Builder

Builder.load_string("""
<EditBorderImage>:
    padding: 0, 0, int(app.button_scale / 2), 0
    id: editBorder
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
        disabled: not root.owner.edit_border
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
            text: 'Border Overlays:'
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
                text: 'Border Opacity:'
            NormalButton:
                text: 'Reset'
                on_release: root.reset_border_opacity()
        HalfSlider:
            id: opacitySlider
            value: root.border_opacity
            on_value: root.border_opacity = self.value
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            LeftNormalLabel:
                text: 'X Size:'
            NormalButton:
                text: 'Reset'
                on_release: root.reset_border_x_scale()
        NormalSlider:
            id: borderXScale
            value: root.border_x_scale
            on_value: root.border_x_scale = self.value
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            LeftNormalLabel:
                text: 'Y Size:'
            NormalButton:
                text: 'Reset'
                on_release: root.reset_border_y_scale()
        NormalSlider:
            id: borderYScale
            value: root.border_y_scale
            on_value: root.border_y_scale = self.value
        SmallBufferY:
        LeftNormalLabel:
            text: 'Select A Border:'
            height: app.button_scale
            size_hint_y: None
        BoxLayout:
            canvas.before:
                Color:
                    rgba: app.theme.area_background
                BorderImage:
                    pos: self.pos
                    size: self.size
                    source: 'data/buttonflat.png'
            orientation: 'horizontal'
            size_hint_y: None
            height: int(app.button_scale * 10)
            Scroller:
                id: wrapper
                NormalTreeView:
                    id: borders
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
                text: 'Border Tinting:'
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


class EditBorderImage(GridLayout):
    """Panel to expose image border overlays."""

    selected = StringProperty()
    border_x_scale = NumericProperty(0)
    border_y_scale = NumericProperty(0)
    border_opacity = NumericProperty(1)
    tint = ListProperty([1.0, 1.0, 1.0, 1.0])

    owner = ObjectProperty()
    borders = ListProperty()
    type = StringProperty()
    preset_name = StringProperty()

    def __init__(self, **kwargs):
        Clock.schedule_once(self.add_video_preset)
        Clock.schedule_once(self.populate_borders)
        super(EditBorderImage, self).__init__(**kwargs)

    def refresh_buttons(self):
        pass

    def add_video_preset(self, *_):
        if not self.owner.view_image:
            video_preset = self.ids['videoPreset']
            video_preset.add_widget(VideoEncodePreset())

    def save_last(self):
        self.owner.edit_border = True
        self.owner.border_selected = self.selected
        self.owner.border_x_scale = self.border_x_scale
        self.owner.border_y_scale = self.border_y_scale
        self.owner.border_opacity = self.border_opacity
        self.owner.border_tint = self.tint

    def load_last(self):
        self.selected = self.owner.border_selected
        self.border_x_scale = self.owner.border_x_scale
        self.border_y_scale = self.owner.border_y_scale
        self.border_opacity = self.owner.border_opacity
        self.tint = self.owner.border_tint

    def on_selected(self, *_):
        if self.selected:
            border_index = int(self.selected)
        else:
            border_index = 0
        self.reset_border_x_scale()
        self.reset_border_y_scale()
        if border_index == 0:
            self.owner.viewer.edit_image.border_image = []
        else:
            self.owner.viewer.edit_image.border_image = self.borders[border_index]

    def populate_borders(self, *_):
        self.borders = [None]
        for file in os.listdir('borders'):
            if file.endswith('.txt'):
                border_name = os.path.splitext(file)[0]
                border_sizes = []
                border_images = []
                with open(os.path.join('borders', file)) as input_file:
                    for line in input_file:
                        if ':' in line and not line.startswith('#'):
                            size, image = line.split(':')
                            border_sizes.append(float(size))
                            border_images.append(image.strip())
                if border_sizes:
                    self.borders.append([border_name, border_sizes, border_images])

        borders_tree = self.ids['borders']
        nodes = list(borders_tree.iterate_all_nodes())
        for node in nodes:
            borders_tree.remove_node(node)

        for index, border in enumerate(self.borders):
            if border:
                node = TreeViewButton(dragable=False, owner=self, target=str(index), folder_name=border[0])
                borders_tree.add_node(node)
            else:
                node = TreeViewButton(dragable=False, owner=self, target=str(index), folder_name='None')
                borders_tree.add_node(node)
                borders_tree.select_node(node)

    def on_border_x_scale(self, *_):
        self.owner.viewer.edit_image.border_x_scale = self.border_x_scale

    def reset_border_x_scale(self):
        self.border_x_scale = 0

    def on_border_y_scale(self, *_):
        self.owner.viewer.edit_image.border_y_scale = self.border_y_scale

    def reset_border_y_scale(self):
        self.border_y_scale = 0

    def on_border_opacity(self, *_):
        self.owner.viewer.edit_image.border_opacity = self.border_opacity

    def reset_border_opacity(self, *_):
        self.border_opacity = 1

    def on_tint(self, *_):
        self.owner.viewer.edit_image.border_tint = self.tint

    def reset_tint(self):
        self.tint = [1.0, 1.0, 1.0, 1.0]