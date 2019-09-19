from io import BytesIO

from kivy.app import App
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.gridlayout import GridLayout

from generalcommands import to_bool
from kivy.lang.builder import Builder

Builder.load_string("""
<EditDenoiseImage>:
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
            on_release: root.save_image()
        WideButton:
            text: 'Cancel Edit'
            warn: True
            on_release: root.owner.set_edit_panel('main')
    WideButton:
        id: loadLast
        disabled: not root.owner.edit_denoise
        text: "Load Last Settings"
        on_release: root.load_last()
    MediumBufferY:
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        LeftNormalLabel:
            text: 'Denoise Image:'
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
        #NormalButton:
        #    size_hint_x: 1
        #    text: 'Generate Full Preview'
        #    on_release: root.denoise()
        FloatLayout:
            canvas.before:
                Color:
                    rgba:0,0,0,1
                Rectangle:
                    size: self.size
                    pos: self.pos
            size_hint_y: None
            height: self.width
            ScrollViewCentered:
                canvas.after:
                    Color:
                        rgba: self.bar_color[:3] + [self.bar_color[3] * 1 if self.do_scroll_y else 0]
                    Rectangle:
                        pos: self.right - self.bar_width - self.bar_margin, self.y + self.height * self.vbar[0]
                        size: self.bar_width, self.height * self.vbar[1]
                    Color:
                        rgba: self.bar_color[:3] + [self.bar_color[3] * 1 if self.do_scroll_x else 0]
                    Rectangle:
                        pos: self.x + self.width * self.hbar[0], self.y + self.bar_margin
                        size: self.width * self.hbar[1], self.bar_width
                on_scroll_stop: root.update_preview()
                pos: self.parent.pos
                size: self.parent.size
                scroll_type: ['bars', 'content']
                id: wrapper
                size_hint: 1, 1
                bar_width: int(app.button_scale * .75)
                bar_color: app.theme.scroller_selected
                bar_inactive_color: app.theme.scroller
                RelativeLayout:
                    owner: root
                    size_hint: None, None
                    size: root.image_x, root.image_y
                    Image:
                        allow_stretch: True
                        size: root.image_x, root.image_y
                        size_hint: None, None
                        id: noisePreview
                        mipmap: True
                        #source: root.imagefile
                    Image:
                        id: denoiseOverlay
                        size: self.parent.parent.size
                        size_hint: None, None
                        opacity: 0

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            NormalLabel:
                text: 'Luminance: '
            IntegerInput:
                text: root.luminance_denoise
                on_text: root.luminance_denoise = self.text
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            NormalLabel:
                text: 'Color: '
            IntegerInput:
                text: root.color_denoise
                on_text: root.color_denoise = self.text
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            NormalLabel:
                text: 'Search Size: '
            IntegerInput:
                text: root.search_window
                on_text: root.search_window = self.text
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: app.button_scale
            NormalLabel:
                text: 'Noise Size: '
            IntegerInput:
                on_text: root.block_size = self.text
""")

class EditDenoiseImage(GridLayout):
    """Panel to expose image denoise options."""

    luminance_denoise = StringProperty('10')
    color_denoise = StringProperty('10')
    search_window = StringProperty('15')
    block_size = StringProperty('5')

    owner = ObjectProperty()
    imagefile = StringProperty('')
    image_x = NumericProperty(1)
    image_y = NumericProperty(1)
    full_image = ObjectProperty()

    def __init__(self, **kwargs):
        Clock.schedule_once(self.update_preview)
        super(EditDenoiseImage, self).__init__(**kwargs)

    def refresh_buttons(self):
        pass

    def save_last(self):
        self.owner.edit_denoise = True
        self.owner.luminance_denoise = self.luminance_denoise
        self.owner.color_denoise = self.color_denoise
        self.owner.search_window = self.search_window
        self.owner.block_size = self.block_size

    def load_last(self):
        self.luminance_denoise = self.owner.luminance_denoise
        self.color_denoise = self.owner.color_denoise
        self.search_window = self.owner.search_window
        self.block_size = self.owner.block_size

    def save_image(self):
        self.owner.viewer.edit_image.denoise = True
        if self.owner.viewer.edit_image.video:
            self.owner.save_video()
        else:
            self.owner.save_image()

    def reset_all(self):
        """Reset all edit values to defaults."""
        self.luminance_denoise = '10'
        self.color_denoise = '10'
        self.search_window = '21'
        self.block_size = '7'

    def on_luminance_denoise(self, *_):
        if not self.luminance_denoise:
            luminance_denoise = 0
        else:
            luminance_denoise = int(self.luminance_denoise)
        self.owner.viewer.edit_image.luminance_denoise = luminance_denoise
        self.update_preview()

    def on_color_denoise(self, *_):
        if not self.color_denoise:
            color_denoise = 0
        else:
            color_denoise = int(self.color_denoise)
        self.owner.viewer.edit_image.color_denoise = color_denoise
        self.update_preview()

    def on_search_window(self, *_):
        if not self.search_window:
            search_window = 0
        else:
            search_window = int(self.search_window)
        if (search_window % 2) == 0:
            search_window = search_window + 1
        self.owner.viewer.edit_image.search_window = search_window
        self.update_preview()

    def on_block_size(self, *_):
        if not self.block_size:
            block_size = 0
        else:
            block_size = int(self.block_size)
        if (block_size % 2) == 0:
            block_size = block_size + 1
        self.owner.viewer.edit_image.block_size = block_size
        self.update_preview()

    def update_preview(self, *_):
        #Gets the denoised preview image and updates it in the ui

        #convert pil image to bytes and display background image
        app = App.get_running_app()
        if to_bool(app.config.get("Settings", "lowmem")):
            image = self.owner.viewer.edit_image.edit_image
        else:
            image = self.owner.viewer.edit_image.original_image
        noise_preview = self.ids['noisePreview']
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image_bytes = BytesIO()
        image.save(image_bytes, 'jpeg')
        image_bytes.seek(0)
        noise_preview._coreimage = CoreImage(image_bytes, ext='jpg')
        noise_preview._on_tex_change()

        #update overlay image
        scroll_area = self.ids['wrapper']
        width = scroll_area.size[0]
        height = scroll_area.size[1]
        pos_x = int((self.image_x * scroll_area.scroll_x) - (width * scroll_area.scroll_x))
        image_pos_y = self.image_y - int((self.image_y * scroll_area.scroll_y) + (width * (1 - scroll_area.scroll_y)))
        preview = self.owner.viewer.edit_image.denoise_preview(width, height, pos_x, image_pos_y)
        overlay_image = self.ids['denoiseOverlay']
        widget_pos_y = int((self.image_y * scroll_area.scroll_y) - (width * scroll_area.scroll_y))
        overlay_image.pos = [pos_x, widget_pos_y]
        overlay_image._coreimage = CoreImage(preview, ext='jpg')
        overlay_image._on_tex_change()
        overlay_image.opacity = 1

    def denoise(self):
        """Generates a preview using the current denoise settings"""

        self.owner.viewer.edit_image.update_preview(denoise=True)