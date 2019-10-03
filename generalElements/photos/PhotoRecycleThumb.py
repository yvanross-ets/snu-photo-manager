from kivy.animation import Animation
from kivy.app import App
from kivy.properties import ListProperty, BooleanProperty, ObjectProperty, StringProperty, NumericProperty
from kivy.uix.behaviors import DragBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior

from generalcommands import isfile2

from kivy.lang.builder import Builder

Builder.load_string("""
<PhotoRecycleThumb>:
    canvas.before:
        Color:
            rgba: self.underlay_color
            #rgba: app.theme.selected if self.selected else (0, 0, 0, 0)
        Rectangle:
            pos: (self.pos[0]-5, self.pos[1]-5)
            size: (self.size[0]+10, self.size[1]+10)
    canvas.after:
        Color:
            rgba: (1, 1, 1, 0) if self.found else(1, 0, 0, .33)
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: app.theme.favorite if root.favorite else [0, 0, 0, 0]
        Rectangle:
            source: 'data/star.png'
            pos: (self.pos[0]+(self.size[0]/2)-(self.size[0]*.05), self.pos[1]+(self.size[0]*.1))
            size: (self.size[0]*.1, self.size[0]*.1)
        Color:
            rgba: 1, 1, 1, .5 if root.video else 0
        Rectangle:
            source: 'data/play_overlay.png'
            pos: (self.pos[0]+self.width/8, self.pos[1]+self.width/8) if self.title else (self.pos[0]+self.width/4, self.pos[1]+self.width/4)
            size: (self.width/4, self.width/4) if self.title else (self.width/2, self.width/2)

    drag_rectangle: self.x, self.y, self.width, self.height
    drag_timeout: 10000000
    drag_distance: 0
    width: (app.button_scale * 4)
    height: (app.button_scale * 4)
    size_hint_y: None
    size_hint_x: None
    orientation: 'horizontal'
    AsyncThumbnail:
        id: thumbnail
        width: self.height
        size_hint_x: None
""")
class PhotoRecycleThumb(DragBehavior, BoxLayout, RecycleDataViewBehavior):
    """Wrapper widget for image thumbnails.  Used for displaying images in grid views."""

    underlay_color = ListProperty([0, 0, 0, 0])
    found = BooleanProperty(True)  # Used to add a red overlay to the thumbnail if the source file doesn't exist
    owner = ObjectProperty()
    target = StringProperty()
    type = StringProperty('None')
    filename = StringProperty()
    fullpath = StringProperty()
    folder = StringProperty()
    database_folder = StringProperty()
    selected = BooleanProperty(False)
    drag = False
    dragable = BooleanProperty(True)
    image = ObjectProperty()
    photo_orientation = NumericProperty(1)
    angle = NumericProperty(0)  # used to display the correct orientation of the image
    favorite = BooleanProperty(False)  # if True, a star overlay will be displayed on the image
    video = BooleanProperty(False)
    source = StringProperty()
    photoinfo = ListProperty()
    temporary = BooleanProperty(False)
    title = StringProperty('')
    view_album = BooleanProperty(True)
    mirror = BooleanProperty(False)
    index = NumericProperty(0)
    data = {}

    def on_selected(self, *_):
        app = App.get_running_app()
        if self.selected:
            new_color = app.theme.selected
        else:
            new_color = [0, 0, 0, 0]
        if app.animations:
            anim = Animation(underlay_color=new_color, duration=app.animation_length)
            anim.start(self)
        else:
            self.underlay_color = new_color

    def refresh_view_attrs(self, rv, index, data):
        """Called when widget is loaded into recycleview layout"""
        self.index = index
        self.data = data
        thumbnail = self.ids['thumbnail']
        thumbnail.temporary = self.data['temporary']
        thumbnail.photo = self.data['photo']
        thumbnail.source = self.data['source']
        self.image = thumbnail
        return super(PhotoRecycleThumb, self).refresh_view_attrs(rv, index, data)

    def on_source(self, *_):
        """Sets up the display image when first loaded."""

        found = isfile2(self.source)
        self.found = found
        if self.photo_orientation in [2, 4, 5, 7]:
            self.mirror = True
        else:
            self.mirror = False
        if self.photo_orientation == 3 or self.photo_orientation == 4:
            self.angle = 180
        elif self.photo_orientation == 5 or self.photo_orientation == 6:
            self.angle = 270
        elif self.photo_orientation == 7 or self.photo_orientation == 8:
            self.angle = 90
        else:
            self.angle = 0

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected

    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        if self.collide_point(*touch.pos):
            if touch.is_double_tap:
                if not self.temporary and self.view_album:
                    app = App.get_running_app()
                    if not app.shift_pressed:
                        app.show_album(self)
                        return
            app = App.get_running_app()
            if app.shift_pressed:
                self.parent.select_range(self.index, touch)
                return
            self.parent.select_with_touch(self.index, touch)
            self.owner.update_selected()
            if self.dragable:
                thumbnail = self.ids['thumbnail']
                self.drag = True
                app = App.get_running_app()
                temp_coords = self.to_parent(touch.opos[0], touch.opos[1])
                widget_coords = (temp_coords[0] - thumbnail.pos[0], temp_coords[1] - thumbnail.pos[1])
                window_coords = self.to_window(touch.pos[0], touch.pos[1])
                app.drag(self, 'start', window_coords, image=self.image, offset=widget_coords, fullpath=self.fullpath)

    def on_touch_move(self, touch):
        #super().on_touch_move(touch)
        if self.drag:
            if not self.selected:
                self.parent.select_node(self.index)
                self.owner.update_selected()
            app = App.get_running_app()
            window_coords = self.to_window(touch.pos[0], touch.pos[1])
            app.drag(self, 'move', window_coords)

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        if self.drag:
            app = App.get_running_app()
            window_coords = self.to_window(touch.pos[0], touch.pos[1])
            app.drag(self, 'end', window_coords)
            self.drag = False