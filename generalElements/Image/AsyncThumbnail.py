import os
from io import BytesIO

from PIL import Image
from kivy.app import App
from kivy.cache import Cache
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage, ImageLoader
from kivy.core.image.img_pil import ImageLoaderPIL
from kivy.core.window import Window
from kivy.loader import Loader as ThumbLoader
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, ObjectProperty
from kivy.uix.image import Image as KivyImage

from generalcommands import isfile2, to_bool
from kivy.lang.builder import Builder

Builder.load_string("""

<AsyncThumbnail>:
    canvas.before:
        PushMatrix
        Rotate:
            angle: self.angle
            axis: 0,0,1
            origin: self.center
    canvas.after:
        PopMatrix
    allow_stretch: True""")

class AsyncThumbnail(KivyImage):
    """AsyncThumbnail is a modified version of the kivy AsyncImage class,
    used to automatically generate and save thumbnails of a specified image.
    """

    loadfullsize = BooleanProperty(False)  #Enable loading the full-sized image, thumbnail will be displayed temporarily
    temporary = BooleanProperty(False)  #This image is a temporary file, not in the screenDatabase
    photoinfo = ListProperty()  #Photo data of the image
    mirror = BooleanProperty(False)
    loadanyway = BooleanProperty(False)  #Force generating thumbnail even if this widget isnt added to a parent widget
    thumbsize = None
    angle = NumericProperty(0)
    aspect = NumericProperty(1)
    lowmem = BooleanProperty(False)
    thumbnail = ObjectProperty()
    is_full_size = BooleanProperty(False)
    disable_rotate = BooleanProperty(False)

    def __init__(self, **kwargs):
        self._coreimage = None
        self._fullimage = None
        super(AsyncThumbnail, self).__init__(**kwargs)
        self.bind(source=self._load_source)
        if self.source:
            self._load_source()

    def load_thumbnail(self, filename):
        """Load from thumbnail screenDatabase, or generate a new thumbnail of the given image filename.
        Argument:
            filename: Image filename.
        Returns: A Kivy image"""

        root_widget = True
        if root_widget or self.loadanyway:
            app = App.get_running_app()
            full_filename = filename
            photo = self.photoinfo

            file_found = isfile2(full_filename)
            if file_found:
                modified_date = int(os.path.getmtime(full_filename))
                if modified_date > photo[7]:
                    #if not self.temporary:
                    #    app.database_item_update(photo)
                    #    app.update_photoinfo(folders=[photo[1]])
                    app.database_thumbnail_update(photo[0], photo[2], modified_date, photo[13], temporary=self.temporary)
            thumbnail_image = app.database_thumbnail_get(photo[0], temporary=self.temporary)
            if thumbnail_image:
                imagedata = bytes(thumbnail_image[2])
                data = BytesIO()
                data.write(imagedata)
                data.seek(0)
                image = CoreImage(data, ext='jpg')
            else:
                if file_found:
                    updated = app.database_thumbnail_update(photo[0], photo[2], modified_date, photo[13], temporary=self.temporary)
                    if updated:
                        thumbnail_image = app.database_thumbnail_get(photo[0], temporary=self.temporary)
                        data = BytesIO(thumbnail_image[2])
                        image = CoreImage(data, ext='jpg')
                    else:
                        image = ImageLoader.load(full_filename)
                else:
                    image = ImageLoader.load('data/null.jpg')
            return image
        else:
            return ImageLoader.load('data/null.jpg')

    def set_angle(self):
        if not self.disable_rotate:
            orientation = self.photoinfo[13]
            if orientation in [2, 4, 5, 7]:
                self.mirror = True
            else:
                self.mirror = False
            if self.mirror:
                self.texture.flip_horizontal()

            if orientation == 3 or orientation == 4:
                self.angle = 180
            elif orientation == 5 or orientation == 6:
                self.angle = 270
            elif orientation == 7 or orientation == 8:
                self.angle = 90
            else:
                self.angle = 0

    def _load_source(self, *_):
        self.set_angle()
        source = self.source
        photo = self.photoinfo
        self.nocache = True
        if not source and not photo:
            if self._coreimage is not None:
                self._coreimage.unbind(on_texture=self._on_tex_change)
            self.texture = None
            self._coreimage = None
        elif not photo:
            Clock.schedule_once(lambda *dt: self._load_source(), .25)
        else:
            ThumbLoader.max_upload_per_frame = 50
            ThumbLoader.num_workers = 4
            ThumbLoader.loading_image = 'data/loadingthumbnail.png'
            self._coreimage = image = ThumbLoader.image(source, load_callback=self.load_thumbnail, nocache=self.nocache, mipmap=self.mipmap, anim_delay=self.anim_delay)
            image.bind(on_load=self._on_source_load)
            image.bind(on_texture=self._on_tex_change)
            self.texture = image.texture

    def on_loadfullsize(self, *_):
        if self.thumbnail and not self.is_full_size and self.loadfullsize:
            self._on_source_load()

    def _on_source_load(self, *_):
        try:
            image = self._coreimage.image
            if not image:
                return
        except:
            return
        self.thumbnail = image
        self.thumbsize = image.size
        self.texture = image.texture
        self.aspect = image.size[1] / image.size[0]

        if self.loadfullsize:
            Cache.remove('kv.image', self.source)
            try:
                self._coreimage.image.remove_from_cache()
                self._coreimage.remove_from_cache()
            except:
                pass
            Clock.schedule_once(lambda dt: self._load_fullsize())

    def _load_fullsize(self):
        app = App.get_running_app()
        if not self.lowmem:
            low_memory = to_bool(app.config.get("Settings", "lowmem"))
        else:
            low_memory = True
        if not low_memory:
            #load a screen-sized image instead of full-sized to save memory
            if os.path.splitext(self.source)[1].lower() == '.bmp':
                #default image loader messes up bmp files, use pil instead
                self._coreimage = ImageLoaderPIL(self.source)
            else:
                self._coreimage = KivyImage(source=self.source)
        else:
            #load and rescale image
            original_image = Image.open(self.source)
            image = original_image.copy()
            original_image.close()
            resize_width = Window.size[0]
            if image.size[0] > resize_width:
                width = int(resize_width)
                height = int(resize_width * (image.size[1] / image.size[0]))
                if width < 10:
                    width = 10
                if height < 10:
                    height = 10
                image = image.resize((width, height))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image_bytes = BytesIO()
            image.save(image_bytes, 'jpeg')
            image_bytes.seek(0)
            self._coreimage = CoreImage(image_bytes, ext='jpg')

        self.texture = self._coreimage.texture
        if self.mirror:
            self.texture.flip_horizontal()

    def _on_tex_change(self, *largs):
        if self._coreimage:
            self.texture = self._coreimage.texture

    def on_texture(self, *_):
        if self.loadfullsize:
            self.is_full_size = True

    def texture_update(self, *largs):
        pass