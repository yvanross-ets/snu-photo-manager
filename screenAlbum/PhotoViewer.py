from kivy.graphics.transformation import Matrix
from kivy.properties import ListProperty, BooleanProperty, NumericProperty, StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from screenAlbum.customImage import CustomImage
from screenAlbum.RotationGrid import RotationGrid
from screenAlbum.CropOverlay import CropOverlay
from screenAlbum.ExitFullScreenButton import ExitFullscreenButton
from generalElements.photos.StencilViewTouch import StencilViewTouch
from generalElements.views.LimitedScatterLayout import LimitedScatterLayout
from screenAlbum.PhotoShow import PhotoShow
from generalElements.images.AsyncThumbnail import AsyncThumbnail
from generalElements.labels.ShortLabel import ShortLabel

from kivy.lang.builder import Builder

Builder.load_string("""
<PhotoViewer>:
    orientation: 'vertical'
    StencilViewTouch:
        size_hint_y: 1
        canvas.after:
            Color:
                rgba: app.theme.favorite if root.favorite else [0, 0, 0, 0]
            Rectangle:
                source: 'data/star.png'
                pos: self.width - (self.width*.03), 0
                size: (self.width*.03, self.width*.03)
        id: photoStencil
        LimitedScatterLayout:
            bypass: root.bypass
            id: wrapper
            size: photoStencil.size
            size_hint: None, None
            scale_min: 1
            scale_max: root.scale_max
            do_rotation: False
            PhotoShow:
                bypass: root.bypass
                id: photoShow
                pos: photoStencil.pos
                size_hint: 1, 1
                AsyncThumbnail:
                    canvas.before:
                        PushMatrix
                        Scale:
                            x: 1 if root.angle == 0 or self.width == 0 else ((self.height/self.width) if (self.height/self.width) > .75 else .75)
                            y: 1 if root.angle == 0 or self.width == 0 else ((self.height/self.width) if (self.height/self.width) > .75 else .75)
                            origin: photoStencil.center
                    canvas.after:
                        PopMatrix
                    photoinfo: root.photoinfo
                    photo_id: root.photo_id
                    loadanyway: True
                    loadfullsize: True
                    source: root.file
                    mirror: root.mirror
                    allow_stretch: True
                    id: image
                    mipmap: True
    BoxLayout:
        opacity: 0 if root.fullscreen or app.simple_interface or root.edit_mode != 'main' else 1
        disabled: True if root.fullscreen or (root.edit_mode != 'main') or app.simple_interface else False
        orientation: 'horizontal'
        size_hint_y: None
        height: 0 if  root.fullscreen or app.simple_interface or root.edit_mode != 'main' else app.button_scale
        Label:
            size_hint_x: .25
        ShortLabel:
            size_hint_y: None
            height: app.button_scale
            text: "Zoom:"
        NormalSlider:
            size_hint_y: None
            height: app.button_scale
            id: zoomSlider
            min: 0
            max: 1
            value: root.zoom
            on_value: root.zoom = self.value
        Label:
            size_hint_x: .25
""")

class PhotoViewer(BoxLayout):
    """Holds the fullsized photo image in album view mode."""

    photoinfo = ListProperty([0, 0])
    favorite = BooleanProperty(False)
    angle = NumericProperty(0)
    mirror = BooleanProperty(False)
    file = StringProperty()
    scale_max = NumericProperty(1)
    edit_mode = StringProperty('main')
    edit_image = ObjectProperty()
    overlay = ObjectProperty(allownone=True)
    bypass = BooleanProperty(False)
    zoom = NumericProperty(0)
    zoompos = ListProperty([0, 0])
    fullscreen = BooleanProperty(False)
    _fullscreen_state = None
    exit_button = ObjectProperty()
    photo_id = 999

    def on_height(self, *_):
        self.reset_zoompos()

    def reset_zoompos(self):
        self.zoompos = [self.width / 2, self.height / 2]

    def on_zoom(self, *_):
        if self.zoom == 0:
            self.reset_zoompos()
        scale_max = self.scale_max
        scale_size = 1 + ((scale_max - 1) * self.zoom)
        scale = Matrix().scale(scale_size, scale_size, scale_size)
        #wrapper = LimitedScatterLayout()
        wrapper = self.ids['wrapper']
        wrapper.transform = Matrix()
        zoompos = self.zoompos
        wrapper.apply_transform(scale, anchor=zoompos)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.edit_mode != 'main' and not self.overlay:
                self.edit_image.opacity = 0
                image = self.ids['image']
                image.opacity = 1
                return True
            else:
                return super(PhotoViewer, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if self.edit_mode != 'main' and not self.overlay:
                self.edit_image.opacity = 1
                image = self.ids['image']
                image.opacity = 0
                return True
            else:
                return super(PhotoViewer, self).on_touch_up(touch)

    def refresh(self):
        """Updates the image subwidget's source file."""

        image = self.ids['image']
        image.source = self.file

    def on_edit_mode(self, *_):
        """Called when the user enters or exits edit mode.
        Adds the edit image widget, and overlay if need be, and sets them up."""

        image = self.ids['image']
        if self.edit_mode == 'main':
            image.opacity = 1
            viewer = self.ids['photoShow']
            if self.edit_image:
                viewer.remove_widget(self.edit_image)
            if self.overlay:
                viewer.remove_widget(self.overlay)
                self.overlay = None
        else:
            image.opacity = 0
            viewer = self.ids['photoShow']
            self.edit_image = CustomImage(source=self.file, mirror=self.mirror, angle=self.angle, photoinfo=self.photoinfo)
            viewer.add_widget(self.edit_image)
            if self.edit_mode == 'rotate':
                #add rotation grid overlay
                self.overlay = RotationGrid()
                viewer.add_widget(self.overlay)
            if self.edit_mode == 'crop':
                #add cropper overlay and set image to crop mode
                self.overlay = CropOverlay(owner=self.edit_image)
                viewer.add_widget(self.overlay)
                self.edit_image.cropping = True
                self.edit_image.cropper = self.overlay

    def stop(self):
        self.fullscreen = False
        #if self.edit_image:
        #    self.edit_image.close_image()

    def close(self):
        pass

    def on_fullscreen(self, instance, value):
        window = self.get_parent_window()
        if value:
            self._fullscreen_state = state = {
                'parent': self.parent,
                'pos': self.pos,
                'size': self.size,
                'pos_hint': self.pos_hint,
                'size_hint': self.size_hint,
                'window_children': window.children[:]}

            #remove all window children
            for child in window.children[:]:
                window.remove_widget(child)

            #put the video in fullscreen
            if state['parent'] is not window:
                state['parent'].remove_widget(self)
            window.add_widget(self)

            #ensure the widget is in 0, 0, and the size will be readjusted
            self.pos = (0, 0)
            self.size = (100, 100)
            self.pos_hint = {}
            self.size_hint = (1, 1)
            self.exit_button = ExitFullscreenButton(owner=self)
            window.add_widget(self.exit_button)

        else:
            state = self._fullscreen_state
            window.remove_widget(self)
            window.remove_widget(self.exit_button)
            for child in state['window_children']:
                window.add_widget(child)
            self.pos_hint = state['pos_hint']
            self.size_hint = state['size_hint']
            self.pos = state['pos']
            self.size = state['size']
            if state['parent'] is not window:
                state['parent'].add_widget(self)