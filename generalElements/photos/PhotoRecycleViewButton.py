from kivy.properties import BooleanProperty, StringProperty, ListProperty

from generalcommands import isfile2
from generalElements.views.RecycleItem import RecycleItem
from kivy.lang.builder import Builder

Builder.load_string("""
<PhotoRecycleViewButton>:
    canvas.after:
        Color:
            rgba: (1, 1, 1, 0) if self.found else(1, 0, 0, .33)
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: app.theme.favorite if self.favorite else [0, 0, 0, 0]
        Rectangle:
            source: 'data/star.png'
            pos: (self.pos[0]+(self.width-(self.height*.5)), self.pos[1]+(self.height*.5)-(self.height*.167))
            size: (self.height*.33, self.height*.33)
        Color:
            rgba: 1, 1, 1, .5 if self.video else 0
        Rectangle:
            source: 'data/play_overlay.png'
            pos: (self.pos[0]+(self.height*.25)), (self.pos[1]+(self.height*.25))
            size: (self.height*.5), (self.height*.5)
    size_hint_x: 1
    height: (app.button_scale * 2)
    AsyncThumbnail:
        id: thumbnail
        #photoinfo: root.photoinfo
        #source: root.source
        size_hint: None, None
        width: (app.button_scale * 2)
        height: (app.button_scale * 2)
    NormalLabel:
        mipmap: True
        size_hint_y: None
        height: (app.button_scale * 2)
        text_size: (self.width - 20, None)
        text: root.text
        halign: 'left'
        valign: 'center'
""")

class PhotoRecycleViewButton(RecycleItem):
    video = BooleanProperty(False)
    favorite = BooleanProperty(False)
    fullpath = StringProperty()
    photoinfo = ListProperty()
    source = StringProperty()
    selectable = BooleanProperty(True)
    found = BooleanProperty(True)

    def on_source(self, *_):
        """Sets up the display image when first loaded."""

        found = isfile2(self.source)
        self.found = found

    def refresh_view_attrs(self, rv, index, data):
        super(PhotoRecycleViewButton, self).refresh_view_attrs(rv, index, data)
        thumbnail = self.ids['thumbnail']
        thumbnail.photoinfo = self.data['photoinfo']
        thumbnail.source = self.data['source']

    def on_touch_down(self, touch):
        super(PhotoRecycleViewButton, self).on_touch_down(touch)
        if self.collide_point(*touch.pos) and self.selectable:
            self.owner.fullpath = self.fullpath
            self.owner.photo = self.source
            self.parent.selected = self.data
            return True