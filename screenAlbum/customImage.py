try:
    import numpy
    import cv2
    opencv = True
except:
    opencv = False
import math
import PIL
from PIL import Image, ImageEnhance, ImageOps, ImageChops, ImageDraw, ImageFilter, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import os
from io import BytesIO

from ffpyplayer.player import MediaPlayer
from ffpyplayer.pic import SWScale
from kivy.config import Config
Config.window_icon = "data/icon.png"
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.uix.image import Image as KivyImage
from kivy.core.image import Image as CoreImage
from generalcommands import rotated_rect_with_max_area
from generalconstants import *

from kivy.lang.builder import Builder
Builder.load_string("""
<CustomImage>:
    allow_stretch: True
""")

class CustomImage(KivyImage):
    """Custom image display widget.
    Enables editing operations, displaying them in real-time using a low resolution preview of the original image file.
    All editing variables are watched by the widget and it will automatically update the preview when they are changed.
    """

    exif = ''
    pixel_format = ''
    length = NumericProperty(0)
    framerate = ListProperty()
    video = BooleanProperty(False)
    player = ObjectProperty(None, allownone=True)
    position = NumericProperty(0.0)
    start_point = NumericProperty(0.0)
    end_point = NumericProperty(1.0)
    original_image = ObjectProperty()
    photoinfo = ListProperty()
    original_width = NumericProperty(0)
    original_height = NumericProperty(0)
    flip_horizontal = BooleanProperty(False)
    flip_vertical = BooleanProperty(False)
    mirror = BooleanProperty(False)
    angle = NumericProperty(0)
    rotate_angle = NumericProperty(0)
    fine_angle = NumericProperty(0)
    brightness = NumericProperty(0)
    shadow = NumericProperty(0)
    contrast = NumericProperty(0)
    gamma = NumericProperty(0)
    saturation = NumericProperty(0)
    temperature = NumericProperty(0)
    tint = ListProperty([1.0, 1.0, 1.0, 1.0])
    curve = ListProperty()
    crop_top = NumericProperty(0)
    crop_bottom = NumericProperty(0)
    crop_left = NumericProperty(0)
    crop_right = NumericProperty(0)
    filter = StringProperty('')
    filter_amount = NumericProperty(0)
    autocontrast = BooleanProperty(False)
    equalize = NumericProperty(0)
    histogram = ListProperty()
    edit_image = ObjectProperty()
    cropping = BooleanProperty(False)
    touch_point = ObjectProperty()
    active_cropping = BooleanProperty(False)
    crop_start = ListProperty()
    sharpen = NumericProperty(0)
    bilateral = NumericProperty(0.5)
    bilateral_amount = NumericProperty(0)
    median_blur = NumericProperty(0)
    vignette_amount = NumericProperty(0)
    vignette_size = NumericProperty(.5)
    edge_blur_amount = NumericProperty(0)
    edge_blur_size = NumericProperty(.5)
    edge_blur_intensity = NumericProperty(.5)
    cropper = ObjectProperty()  #Holder for the cropper overlay
    crop_controls = ObjectProperty()  #Holder for the cropper edit panel object
    adaptive_clip = NumericProperty(0)
    border_opacity = NumericProperty(1)
    border_image = ListProperty()
    border_tint = ListProperty([1.0, 1.0, 1.0, 1.0])
    border_x_scale = NumericProperty(.5)
    border_y_scale = NumericProperty(.5)
    crop_min = NumericProperty(100)
    size_multiple = NumericProperty(1)

    #Denoising variables
    denoise = BooleanProperty(False)
    luminance_denoise = NumericProperty(10)
    color_denoise = NumericProperty(10)
    search_window = NumericProperty(15)
    block_size = NumericProperty(5)

    frame_number = 0
    max_frames = 0
    start_seconds = 0
    first_frame = None

    def start_video_convert(self):
        self.close_video()
        self.player = MediaPlayer(self.source, ff_opts={'paused': True, 'ss': 0.0, 'an': True})
        self.player.set_volume(0)
        self.frame_number = 0
        if self.start_point > 0 or self.end_point < 1:
            all_frames = self.length * (self.framerate[0] / self.framerate[1])
            self.max_frames = all_frames * (self.end_point - self.start_point)
        else:
            self.max_frames = 0

        #need to wait for load so the seek routine doesnt crash python
        self.first_frame = self.wait_frame()

        if self.start_point > 0:
            self.start_seconds = self.length * self.start_point
            self.first_frame = self.seek_player(self.start_seconds)

    def wait_frame(self):
        #Ensures that a frame is gotten
        frame = None
        while not frame:
            frame, value = self.player.get_frame(force_refresh=True)
        return frame

    def start_seek(self, seek):
        #tell the player to seek to a position
        self.player.set_pause(False)
        self.player.seek(pts=seek, relative=False, accurate=True)
        self.player.set_pause(True)

    def seek_player(self, seek):
        self.start_seek(seek)

        framerate = self.framerate[0] / self.framerate[1]
        target_seek_frame = seek * framerate

        loops = 0
        total_loops = 0
        while True:
            loops += 1
            total_loops += 1
            if loops > 5:
                #seek has been stuck for a while, try to seek again
                self.start_seek(seek)
                loops = 0
            #check if seek has gotten within a couple frames yet
            frame = self.wait_frame()
            current_seek = frame[1]
            current_seek_frame = current_seek * framerate
            frame_distance = abs(target_seek_frame - current_seek_frame)
            if frame_distance < 2 or total_loops >= 30:
                #seek has finished, or give up after a lot of tries to not freeze the program...
                break
        return frame

    def get_converted_frame(self):
        if self.first_frame:
            frame = self.first_frame
            self.first_frame = None
        else:
            self.player.set_pause(False)
            frame = None
            while not frame:
                frame, value = self.player.get_frame(force_refresh=False)
                if value == 'eof':
                    return None
            self.player.set_pause(True)
        self.frame_number = self.frame_number + 1
        if self.max_frames:
            if self.frame_number > self.max_frames:
                return None
        frame_image = frame[0]
        frame_size = frame_image.get_size()
        frame_converter = SWScale(frame_size[0], frame_size[1], frame_image.get_pixel_format(), ofmt='rgb24')
        new_frame = frame_converter.scale(frame_image)
        image_data = bytes(new_frame.to_bytearray()[0])
        image = Image.frombuffer(mode='RGB', size=(frame_size[0], frame_size[1]), data=image_data, decoder_name='raw')
        #for some reason, video frames are read upside-down? fix it here...
        image = image.transpose(PIL.Image.FLIP_TOP_BOTTOM)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image = self.adjust_image(image, preview=False)
        return [image, frame[1]]

    def close_video(self):
        if self.player:
            self.player.close_player()
            self.player = None

    def open_video(self):
        self.player = MediaPlayer(self.source, ff_opts={'paused': True, 'ss': 1.0, 'an': True})
        frame = None
        while not frame:
            frame, value = self.player.get_frame(force_refresh=True)
        data = self.player.get_metadata()
        self.length = data['duration']
        self.framerate = data['frame_rate']
        self.pixel_format = data['src_pix_fmt']

    def set_aspect(self, aspect_x, aspect_y):
        """Adjusts the cropping of the image to be a given aspect ratio.
        Attempts to keep the image as large as possible
        Arguments:
            aspect_x: Horizontal aspect ratio element, numerical value.
            aspect_y: Vertical aspect ratio element, numerical value.
        """

        width = self.original_width - self.crop_left - self.crop_right
        height = self.original_height - self.crop_top - self.crop_bottom
        if aspect_x != width or aspect_y != height:
            current_ratio = width / height
            target_ratio = aspect_x / aspect_y
            if target_ratio > current_ratio:
                #crop top/bottom, width is the same
                new_height = width / target_ratio
                height_difference = height - new_height
                crop_right = 0
                crop_left = 0
                crop_top = height_difference / 2
                crop_bottom = crop_top
            else:
                #crop sides, height is the same
                new_width = height * target_ratio
                width_difference = width - new_width
                crop_top = 0
                crop_bottom = 0
                crop_left = width_difference / 2
                crop_right = crop_left
        else:
            crop_top = 0
            crop_right = 0
            crop_bottom = 0
            crop_left = 0
        self.crop_top = self.crop_top + crop_top
        self.crop_right = self.crop_right + crop_right
        self.crop_bottom = self.crop_bottom + crop_bottom
        self.crop_left = self.crop_left + crop_left
        self.reset_cropper()

    def crop_percent(self, side, percent):
        texture_width = self.original_width
        texture_height = self.original_height
        crop_min = self.crop_min

        if side == 'top':
            crop_amount = texture_height * percent
            if (texture_height - crop_amount - self.crop_bottom) < crop_min:
                crop_amount = texture_height - self.crop_bottom - crop_min
            self.crop_top = crop_amount
        elif side == 'right':
            crop_amount = texture_width * percent
            if (texture_width - crop_amount - self.crop_left) < crop_min:
                crop_amount = texture_width - self.crop_left - crop_min
            self.crop_right = crop_amount
        elif side == 'bottom':
            crop_amount = texture_height * percent
            if (texture_height - crop_amount - self.crop_top) < crop_min:
                crop_amount = texture_height - self.crop_top - crop_min
            self.crop_bottom = crop_amount
        else:
            crop_amount = texture_width * percent
            if (texture_width - crop_amount - self.crop_right) < crop_min:
                crop_amount = texture_width - self.crop_right - crop_min
            self.crop_left = crop_amount
        self.reset_cropper()
        if self.crop_controls:
            self.crop_controls.update_crop()

    def get_crop_percent(self):
        width = self.original_width
        height = self.original_height
        top_percent = self.crop_top / height
        right_percent = self.crop_right / width
        bottom_percent = self.crop_bottom / height
        left_percent = self.crop_left / width
        return [top_percent, right_percent, bottom_percent, left_percent]

    def get_crop_size(self):
        new_width = self.original_width - self.crop_left - self.crop_right
        new_height = self.original_height - self.crop_top - self.crop_bottom
        new_aspect = new_width / new_height
        old_aspect = self.original_width / self.original_height
        return "Size: "+str(int(new_width))+"x"+str(int(new_height))+", Aspect: "+str(round(new_aspect, 2))+" (Original: "+str(round(old_aspect, 2))+")"

    def reset_crop(self):
        """Sets the crop values back to 0 for all sides"""

        self.crop_top = 0
        self.crop_bottom = 0
        self.crop_left = 0
        self.crop_right = 0
        self.reset_cropper(setup=True)

    def reset_cropper(self, setup=False):
        """Updates the position and size of the cropper overlay object."""

        if self.cropper:
            texture_size = self.get_texture_size()
            texture_top_edge = texture_size[0]
            texture_right_edge = texture_size[1]
            texture_bottom_edge = texture_size[2]
            texture_left_edge = texture_size[3]

            texture_width = (texture_right_edge - texture_left_edge)
            #texture_height = (texture_top_edge - texture_bottom_edge)

            divisor = self.original_width / texture_width
            top_edge = texture_top_edge - (self.crop_top / divisor)
            bottom_edge = texture_bottom_edge + (self.crop_bottom / divisor)
            left_edge = texture_left_edge + (self.crop_left / divisor)
            right_edge = texture_right_edge - (self.crop_right / divisor)
            width = right_edge - left_edge
            height = top_edge - bottom_edge

            self.cropper.pos = [left_edge, bottom_edge]
            self.cropper.size = [width, height]
            if setup:
                self.cropper.max_resizable_width = width
                self.cropper.max_resizable_height = height

    def get_texture_size(self):
        """Returns a list of the texture size coordinates.
        Returns:
            List of numbers: [Top edge, Right edge, Bottom edge, Left edge]
        """

        left_edge = (self.size[0] / 2) - (self.norm_image_size[0] / 2)
        right_edge = left_edge + self.norm_image_size[0]
        bottom_edge = (self.size[1] / 2) - (self.norm_image_size[1] / 2)
        top_edge = bottom_edge + self.norm_image_size[1]
        return [top_edge, right_edge, bottom_edge, left_edge]

    def point_over_texture(self, pos):
        """Checks if the given pos (x,y) value is over the image texture.
        Returns False if not over texture, returns point transformed to texture coordinates if over texture.
        """

        texture_size = self.get_texture_size()
        top_edge = texture_size[0]
        right_edge = texture_size[1]
        bottom_edge = texture_size[2]
        left_edge = texture_size[3]
        if pos[0] > left_edge and pos[0] < right_edge:
            if pos[1] > bottom_edge and pos[1] < top_edge:
                texture_x = pos[0] - left_edge
                texture_y = pos[1] - bottom_edge
                return [texture_x, texture_y]
        return False

    def detect_crop_edges(self, first, second):
        """Given two points, this will detect the proper crop area for the image.
        Arguments:
            first: First crop corner.
            second: Second crop corner.
        Returns a list of cropping values:
            [crop_top, crop_bottom, crop_left, crop_right]
        """

        if first[0] < second[0]:
            left = first[0]
            right = second[0]
        else:
            left = second[0]
            right = first[0]
        if first[1] < second[1]:
            top = second[1]
            bottom = first[1]
        else:
            top = first[1]
            bottom = second[1]
        scale = self.original_width / self.norm_image_size[0]
        crop_top = (self.norm_image_size[1] - top) * scale
        crop_bottom = bottom * scale
        crop_left = left * scale
        crop_right = (self.norm_image_size[0] - right) * scale
        return [crop_top, crop_bottom, crop_left, crop_right]

    def set_crop(self, posx, posy, width, height):
        """Sets the crop values based on the cropper widget."""

        texture_size = self.get_texture_size()
        texture_top_edge = texture_size[0]
        texture_right_edge = texture_size[1]
        texture_bottom_edge = texture_size[2]
        texture_left_edge = texture_size[3]

        left_crop = posx - texture_left_edge
        bottom_crop = posy - texture_bottom_edge
        right_crop = texture_right_edge - width - posx
        top_crop = texture_top_edge - height - posy

        texture_width = (texture_right_edge - texture_left_edge)
        divisor = self.original_width / texture_width
        if left_crop < 0:
            self.crop_left = 0
        else:
            self.crop_left = left_crop * divisor
        if right_crop < 0:
            self.crop_right = 0
        else:
            self.crop_right = right_crop * divisor
        if top_crop < 0:
            self.crop_top = 0
        else:
            self.crop_top = top_crop * divisor
        if bottom_crop < 0:
            self.crop_bottom = 0
        else:
            self.crop_bottom = bottom_crop * divisor
        #self.update_preview(recrop=False)
        if self.crop_controls:
            self.crop_controls.update_crop()

    def on_sharpen(self, *_):
        self.update_preview()

    def on_bilateral(self, *_):
        self.update_preview()

    def on_bilateral_amount(self, *_):
        self.update_preview()

    def on_median_blur(self, *_):
        self.update_preview()

    def on_border_opacity(self, *_):
        self.update_preview()

    def on_border_image(self, *_):
        self.update_preview()

    def on_border_x_scale(self, *_):
        self.update_preview()

    def on_border_y_scale(self, *_):
        self.update_preview()

    def on_vignette_amount(self, *_):
        self.update_preview()

    def on_vignette_size(self, *_):
        self.update_preview()

    def on_edge_blur_amount(self, *_):
        self.update_preview()

    def on_edge_blur_size(self, *_):
        self.update_preview()

    def on_edge_blur_intensity(self, *_):
        self.update_preview()

    def on_rotate_angle(self, *_):
        self.update_preview()

    def on_fine_angle(self, *_):
        self.update_preview()

    def on_flip_horizontal(self, *_):
        self.update_preview()

    def on_flip_vertical(self, *_):
        self.update_preview()

    def on_autocontrast(self, *_):
        self.update_preview()

    def on_adaptive_clip(self, *_):
        self.update_preview()

    def on_equalize(self, *_):
        self.update_preview()

    def on_brightness(self, *_):
        self.update_preview()

    def on_shadow(self, *_):
        self.update_preview()

    def on_gamma(self, *_):
        self.update_preview()

    def on_contrast(self, *_):
        self.update_preview()

    def on_saturation(self, *_):
        self.update_preview()

    def on_temperature(self, *_):
        self.update_preview()

    def on_curve(self, *_):
        self.update_preview()

    def on_tint(self, *_):
        self.update_preview()

    def on_border_tint(self, *_):
        self.update_preview()

    def on_size(self, *_):
        pass

    def on_source(self, *_):
        """The source file has been changed, reload image and regenerate preview."""

        self.video = os.path.splitext(self.source)[1].lower() in movietypes
        if self.video:
            self.open_video()
        self.reload_edit_image()
        self.update_texture(self.edit_image)
        #self.update_preview()

    def on_position(self, *_):
        pass

    def reload_edit_image(self):
        """Regenerate the edit preview image."""
        if self.video:
            if not self.player:
                return
            location = self.length * self.position
            frame = self.seek_player(location)
            frame = frame[0]
            frame_size = frame.get_size()
            pixel_format = frame.get_pixel_format()
            frame_converter = SWScale(frame_size[0], frame_size[1], pixel_format, ofmt='rgb24')
            new_frame = frame_converter.scale(frame)
            image_data = bytes(new_frame.to_bytearray()[0])

            original_image = Image.frombuffer(mode='RGB', size=(frame_size[0], frame_size[1]), data=image_data, decoder_name='raw')
            #for some reason, video frames are read upside-down? fix it here...
            original_image = original_image.transpose(PIL.Image.FLIP_TOP_BOTTOM)
            self.original_width = original_image.size[0]
            self.original_height = original_image.size[1]
            self.original_image = original_image
            image = original_image.copy()

        else:
            original_image = Image.open(self.source)
            try:
                self.exif = original_image.info.get('exif', b'')
            except:
                self.exif = ''
            if self.angle != 0:
                if self.angle == 90:
                    original_image = original_image.transpose(PIL.Image.ROTATE_90)
                if self.angle == 180:
                    original_image = original_image.transpose(PIL.Image.ROTATE_180)
                if self.angle == 270:
                    original_image = original_image.transpose(PIL.Image.ROTATE_270)
            self.original_width = original_image.size[0]
            self.original_height = original_image.size[1]
            image = original_image.copy()
            self.original_image = original_image.copy()
            original_image.close()
        image_width = Window.width * .75
        width = int(image_width)
        height = int(image_width*(image.size[1]/image.size[0]))
        if width < 10:
            width = 10
        if height < 10:
            height = 10
        image = image.resize((width, height))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        self.size_multiple = self.original_width / image.size[0]
        self.edit_image = image
        Clock.schedule_once(self.update_histogram)  #Need to delay this because kivy will mess up the drawing of it on first load.
        #self.histogram = image.histogram()

    def update_histogram(self, *_):
        self.histogram = self.edit_image.histogram()

    def on_texture(self, instance, value):
        if value is not None:
            self.texture_size = list(value.size)
        if self.mirror:
            self.texture.flip_horizontal()

    def denoise_preview(self, width, height, pos_x, pos_y):
        left = pos_x
        right = pos_x + width
        lower = pos_y + width
        upper = pos_y
        original_image = self.original_image
        preview = original_image.crop(box=(left, upper, right, lower))
        if preview.mode != 'RGB':
            preview = preview.convert('RGB')
        preview_cv = cv2.cvtColor(numpy.array(preview), cv2.COLOR_RGB2BGR)
        preview_cv = cv2.fastNlMeansDenoisingColored(preview_cv, None, self.luminance_denoise, self.color_denoise, self.search_window, self.block_size)
        preview_cv = cv2.cvtColor(preview_cv, cv2.COLOR_BGR2RGB)
        preview = Image.fromarray(preview_cv)
        preview_bytes = BytesIO()
        preview.save(preview_bytes, 'jpeg')
        preview_bytes.seek(0)
        return preview_bytes

    def update_preview(self, denoise=False, recrop=True):
        """Update the preview image."""

        image = self.adjust_image(self.edit_image)
        if denoise and opencv:
            open_cv_image = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
            open_cv_image = cv2.fastNlMeansDenoisingColored(open_cv_image, None, self.luminance_denoise, self.color_denoise, self.search_window, self.block_size)
            open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(open_cv_image)

        self.update_texture(image)
        self.histogram = image.histogram()
        if recrop:
            self.reset_cropper(setup=True)

    def adjust_image(self, image, preview=True):
        """Applies all current editing opterations to an image.
        Arguments:
            image: A PIL image.
            preview: Generate edit image in preview mode (faster)
        Returns: A PIL image.
        """

        if not preview:
            orientation = self.photoinfo[13]
            if orientation == 3 or orientation == 4:
                image = image.transpose(PIL.Image.ROTATE_180)
            elif orientation == 5 or orientation == 6:
                image = image.transpose(PIL.Image.ROTATE_90)
            elif orientation == 7 or orientation == 8:
                image = image.transpose(PIL.Image.ROTATE_270)
            if orientation in [2, 4, 5, 7]:
                image = image.transpose(PIL.Image.FLIP_LEFT_RIGHT)
            size_multiple = self.size_multiple
        else:
            size_multiple = 1

        if self.sharpen != 0:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(self.sharpen+1)
        if self.median_blur != 0 and opencv:
            max_median = 10 * size_multiple
            median = int(self.median_blur * max_median)
            if median % 2 == 0:
                median = median + 1
            open_cv_image = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
            open_cv_image = cv2.medianBlur(open_cv_image, median)
            open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(open_cv_image)
        if self.bilateral != 0 and self.bilateral_amount != 0 and opencv:
            diameter = int(self.bilateral * 10 * size_multiple)
            if diameter < 1:
                diameter = 1
            sigma_color = self.bilateral_amount * 100 * size_multiple
            if sigma_color < 1:
                sigma_color = 1
            sigma_space = sigma_color
            open_cv_image = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
            open_cv_image = cv2.bilateralFilter(open_cv_image, diameter, sigma_color, sigma_space)
            open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(open_cv_image)
        if self.vignette_amount > 0 and self.vignette_size > 0:
            vignette = Image.new(mode='RGB', size=image.size, color=(0, 0, 0))
            filter_color = int((1-self.vignette_amount)*255)
            vignette_mixer = Image.new(mode='L', size=image.size, color=filter_color)
            draw = ImageDraw.Draw(vignette_mixer)
            shrink_x = int((self.vignette_size * (image.size[0]/2)) - (image.size[0]/4))
            shrink_y = int((self.vignette_size * (image.size[1]/2)) - (image.size[1]/4))
            draw.ellipse([0+shrink_x, 0+shrink_y, image.size[0]-shrink_x, image.size[1]-shrink_y], fill=255)
            vignette_mixer = vignette_mixer.filter(ImageFilter.GaussianBlur(radius=(self.vignette_amount*60)+60))
            image = Image.composite(image, vignette, vignette_mixer)
        if self.edge_blur_amount > 0 and self.edge_blur_intensity > 0 and self.edge_blur_size > 0:
            blur_image = image.filter(ImageFilter.GaussianBlur(radius=(self.edge_blur_amount*30)))
            filter_color = int((1-self.edge_blur_intensity)*255)
            blur_mixer = Image.new(mode='L', size=image.size, color=filter_color)
            draw = ImageDraw.Draw(blur_mixer)
            shrink_x = int((self.edge_blur_size * (image.size[0]/2)) - (image.size[0]/4))
            shrink_y = int((self.edge_blur_size * (image.size[1]/2)) - (image.size[1]/4))
            draw.ellipse([0+shrink_x, 0+shrink_y, image.size[0]-shrink_x, image.size[1]-shrink_y], fill=255)
            blur_mixer = blur_mixer.filter(ImageFilter.GaussianBlur(radius=(self.edge_blur_amount*30)))
            image = Image.composite(image, blur_image, blur_mixer)
        if self.crop_top != 0 or self.crop_bottom != 0 or self.crop_left != 0 or self.crop_right != 0:
            if preview:
                overlay = Image.new(mode='RGB', size=image.size, color=(0, 0, 0))
                divisor = self.original_width / image.size[0]
                draw = ImageDraw.Draw(overlay)
                draw.rectangle([0, 0, (self.crop_left / divisor), image.size[1]], fill=(255, 255, 255))
                draw.rectangle([0, 0, image.size[0], (self.crop_top / divisor)], fill=(255, 255, 255))
                draw.rectangle([(image.size[0] - (self.crop_right / divisor)), 0, (image.size[0]), image.size[1]],
                               fill=(255, 255, 255))
                draw.rectangle([0, (image.size[1] - (self.crop_bottom / divisor)), image.size[0], image.size[1]],
                               fill=(255, 255, 255))
                bright = ImageEnhance.Brightness(overlay)
                overlay = bright.enhance(.333)
                image = ImageChops.subtract(image, overlay)
            else:
                if self.crop_left >= image.size[0]:
                    crop_left = 0
                else:
                    crop_left = int(self.crop_left)
                if self.crop_top >= image.size[1]:
                    crop_top = 0
                else:
                    crop_top = int(self.crop_top)
                if self.crop_right >= image.size[0]:
                    crop_right = image.size[0]
                else:
                    crop_right = int(image.size[0] - self.crop_right)
                if self.crop_bottom >= image.size[1]:
                    crop_bottom = image.size[1]
                else:
                    crop_bottom = int(image.size[1] - self.crop_bottom)
                if self.video:
                    #ensure that image size is divisible by 2
                    new_width = crop_right - crop_left
                    new_height = crop_bottom - crop_top
                    if new_width % 2 == 1:
                        if crop_right < image.size[0]:
                            crop_right = crop_right + 1
                        else:
                            crop_right = crop_right - 1
                    if new_height % 2 == 1:
                        if crop_bottom < image.size[1]:
                            crop_bottom = crop_bottom + 1
                        else:
                            crop_bottom = crop_bottom - 1
                image = image.crop((crop_left, crop_top, crop_right, crop_bottom))
        if self.flip_horizontal:
            image = image.transpose(PIL.Image.FLIP_LEFT_RIGHT)
        if self.flip_vertical:
            image = image.transpose(PIL.Image.FLIP_TOP_BOTTOM)
        if self.rotate_angle != 0:
            if self.rotate_angle == 90:
                image = image.transpose(PIL.Image.ROTATE_270)
            if self.rotate_angle == 180:
                image = image.transpose(PIL.Image.ROTATE_180)
            if self.rotate_angle == 270:
                image = image.transpose(PIL.Image.ROTATE_90)
        if self.fine_angle != 0:
            total_angle = -self.fine_angle*10
            angle_radians = math.radians(abs(total_angle))
            width, height = rotated_rect_with_max_area(image.size[0], image.size[1], angle_radians)
            x = int((image.size[0] - width) / 2)
            y = int((image.size[1] - height) / 2)
            if preview:
                image = image.rotate(total_angle, expand=False)
            else:
                image = image.rotate(total_angle, resample=PIL.Image.BICUBIC, expand=False)
            image = image.crop((x, y, image.size[0] - x, image.size[1] - y))
        if self.autocontrast:
            image = ImageOps.autocontrast(image)
        if self.equalize != 0:
            equalize_image = ImageOps.equalize(image)
            image = Image.blend(image, equalize_image, self.equalize)
        temperature = int(round(abs(self.temperature)*100))
        if temperature != 0:
            temperature = temperature-1
            if self.temperature > 0:
                kelvin = negative_kelvin[99-temperature]
            else:
                kelvin = positive_kelvin[temperature]
            matrix = ((kelvin[0]/255.0), 0.0, 0.0, 0.0,
                      0.0, (kelvin[1]/255.0), 0.0, 0.0,
                      0.0, 0.0, (kelvin[2]/255.0), 0.0)
            image = image.convert('RGB', matrix)
        if self.brightness != 0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1+self.brightness)
        if self.shadow != 0:
            if self.shadow < 0:
                floor = int(abs(self.shadow) * 128)
                table = [0] * floor
                remaining_length = 256 - floor
                for index in range(0, remaining_length):
                    value = int(round((index / remaining_length) * 256))
                    table.append(value)
                lut = table * 3
            else:
                floor = int(abs(self.shadow) * 128)
                table = []
                for index in range(0, 256):
                    percent = 1 - (index / 255)
                    value = int(round(index + (floor * percent)))
                    table.append(value)
                lut = table * 3
            image = image.point(lut)

        if self.gamma != 0:
            if self.gamma == -1:
                gamma = 99999999999999999
            elif self.gamma < 0:
                gamma = 1/(self.gamma+1)
            elif self.gamma > 0:
                gamma = 1/((self.gamma+1)*(self.gamma+1))
            else:
                gamma = 1
            lut = [pow(x/255, gamma) * 255 for x in range(256)]
            lut = lut*3
            image = image.point(lut)
        if self.contrast != 0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1 + self.contrast)
        if self.saturation != 0:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1+self.saturation)
        if self.tint != [1.0, 1.0, 1.0, 1.0]:
            matrix = (self.tint[0], 0.0, 0.0, 0.0,
                      0.0, self.tint[1], 0.0, 0.0,
                      0.0, 0.0, self.tint[2], 0.0)
            image = image.convert('RGB', matrix)
        if self.curve:
            lut = self.curve*3
            image = image.point(lut)

        if self.denoise and not preview and opencv:
            open_cv_image = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
            open_cv_image = cv2.fastNlMeansDenoisingColored(open_cv_image, None, self.luminance_denoise, self.color_denoise, self.search_window, self.block_size)
            open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(open_cv_image)

        if self.adaptive_clip > 0 and opencv:
            open_cv_image = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2Lab)
            channels = cv2.split(open_cv_image)
            clahe = cv2.createCLAHE(clipLimit=(self.adaptive_clip * 4), tileGridSize=(8, 8))
            clahe_image = clahe.apply(channels[0])
            channels[0] = clahe_image
            open_cv_image = cv2.merge(channels)
            open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_Lab2RGB)
            image = Image.fromarray(open_cv_image)

        if self.border_image:
            image_aspect = image.size[0]/image.size[1]
            closest_aspect = min(self.border_image[1], key=lambda x: abs(x-image_aspect))
            index = self.border_image[1].index(closest_aspect)
            image_file = os.path.join('borders', self.border_image[2][index])
            if preview:
                resample = PIL.Image.NEAREST
            else:
                resample = PIL.Image.BICUBIC
            border_image = Image.open(image_file)
            border_crop_x = int(border_image.size[0] * ((self.border_x_scale + 1) / 15))
            border_crop_y = int(border_image.size[1] * ((self.border_y_scale + 1) / 15))
            border_image = border_image.crop((border_crop_x, border_crop_y, border_image.size[0] - border_crop_x,
                                              border_image.size[1] - border_crop_y))
            border_image = border_image.resize(image.size, resample)

            if os.path.splitext(image_file)[1].lower() == '.jpg':
                alpha_file = os.path.splitext(image_file)[0]+'-mask.jpg'
                if not os.path.exists(alpha_file):
                    alpha_file = image_file
                alpha = Image.open(alpha_file)
                alpha = alpha.convert('L')
                alpha = alpha.crop((border_crop_x, border_crop_y, alpha.size[0] - border_crop_x,
                                    alpha.size[1] - border_crop_y))
                alpha = alpha.resize(image.size, resample)
            else:
                alpha = border_image.split()[-1]
                border_image = border_image.convert('RGB')
            if self.border_tint != [1.0, 1.0, 1.0, 1.0]:
                matrix = (self.border_tint[0], 0.0, 0.0, 1.0,
                          0.0, self.border_tint[1], 0.0, 1.0,
                          0.0, 0.0, self.border_tint[2], 1.0)
                border_image = border_image.convert('RGB', matrix)

            enhancer = ImageEnhance.Brightness(alpha)
            alpha = enhancer.enhance(self.border_opacity)
            image = Image.composite(border_image, image, alpha)

        return image

    def update_texture(self, image):
        """Saves a PIL image to the visible texture.
        Argument:
            image: A PIL image
        """

        image_bytes = BytesIO()
        image.save(image_bytes, 'jpeg')
        image_bytes.seek(0)
        self._coreimage = CoreImage(image_bytes, ext='jpg')
        self._on_tex_change()

    def get_full_quality(self):
        """Generate a full sized and full quality version of the source image.
        Returns: A PIL image.
        """

        image = self.original_image.copy()
        if not self.video:
            if self.angle != 0:
                if self.angle == 90:
                    image = image.transpose(PIL.Image.ROTATE_90)
                if self.angle == 180:
                    image = image.transpose(PIL.Image.ROTATE_180)
                if self.angle == 270:
                    image = image.transpose(PIL.Image.ROTATE_270)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image = self.adjust_image(image, preview=False)
        return image

    def close_image(self):
        self.original_image.close()
