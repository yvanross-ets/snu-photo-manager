import time

from kivy.app import App
from kivy.properties import BooleanProperty, StringProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior

from generalconstants import drag_delay
from generalElements.views.RecycleItem import RecycleItem
from kivy.lang.builder import Builder
from models.PhotosTags import Tag,Folder,Photo

Builder.load_string("""
<RecycleTreeViewButton>:
    orientation: 'vertical'
    size_hint_y: None
    #height: int((app.button_scale * 1.5 if self.subtext else app.button_scale) + (app.button_scale * .1 if self.end else 0))
    BoxLayout:
        orientation: 'horizontal'
        Widget:
            width: (app.button_scale * .25) + (app.button_scale * 0.5 * root.indent)
            size_hint_x: None
        Image:
            width: self.texture_size[0]
            size_hint_x: None
            source: 'data/tree_opened.png' if root.expanded else 'data/tree_closed.png'
            opacity: 1 if root.expandable else 0
        BoxLayout:
            orientation: 'vertical'
            NormalLabel:
                id: mainText
                markup: True
                text_size: (self.width - 20, None)
                halign: 'left'
                text: ''
            NormalLabel:
                id: subtext
                text_size: (self.width - 20, None)
                font_size: app.text_scale
                color: .66, .66, .66, 1
                halign: 'left'
                size_hint_y: None
                height: app.button_scale * .5 if root.subtext else 0
                text: root.subtext
    Widget:
        canvas.before:
            Color:
                rgba: 0, 0, 0, .2 if root.end else 0
            Rectangle:
                pos: self.pos
                size: self.size
        size_hint_y: None
        height: int(app.button_scale * .1) if root.end else 0
""")

class RecycleTreeViewButton(ButtonBehavior, RecycleItem):
    """Widget that displays a specific folder, album, or tag in the screenDatabase treeview.
    Responds to clicks and double-clicks.
    """

    displayable = BooleanProperty(True)
    target = StringProperty()  #Folder, Album, Tag, or Person
    #fullpath = StringProperty()  #Folder name, used only on folder type targets
    folder = StringProperty()
    database_folder = StringProperty()
    type = StringProperty()  #The type the target is: folder, album, tag, extra
    total_photos = StringProperty()
    folder_name = StringProperty()
    subtext = StringProperty()
    total_photos_numeric = NumericProperty(0)
    drag = False
    dragable = BooleanProperty(False)
    droptype = StringProperty('folder')
    indent = NumericProperty(0)
    expanded = BooleanProperty(True)
    expandable = BooleanProperty(False)
    end = BooleanProperty(False)

    def refresh_view_attrs(self, rv, index, data):
        """Called when widget is loaded into recycleview layout"""

        app = App.get_running_app()
       # if data.displayable:
        photos = data.item.photos

        if hasattr(data.item,'name'):
            self.ids['mainText'].text = data.item.name
        else:
            self.ids['mainText'].text = data.item.name2()

        if hasattr(data.item, 'nb_photos'):
            self.ids['mainText'].text = self.ids['mainText'].text + ' [b]' + str(data.item.nb_photos) + '[/b]'

        return super(RecycleTreeViewButton, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        app = App.get_running_app()
        if self.collide_point(*touch.pos):
            if touch.is_double_tap and not app.shift_pressed:
                if self.displayable:
                    if self.total_photos_numeric > 0:
                        app.show_album(self)
            else:
                self.parent.selected = {}
                self.parent.selected = self.data.displayable_dict()
                self.on_press()
            if self.dragable:
                self.drag = True
                app = App.get_running_app()
                temp_coords = self.to_parent(touch.opos[0], touch.opos[1])
                widget_coords = (temp_coords[0]-self.pos[0], temp_coords[1]-self.pos[1])
                window_coords = self.to_window(touch.opos[0], touch.opos[1])
                app.drag_treeview(self, 'start', window_coords, offset=widget_coords)

    def on_press(self):
        self.owner.type = self.type
        self.owner.displayable = self.displayable
        self.owner.selected_item = self.item
#        self.owner.selected = self  # will call screenDatabase.On_selected
        photoListRecyclerView = self.owner.ids['screenDatabase']
        photoListRecyclerView.accept(self.data)

        #if hasattr(self.item,'name'):
        #    self.owner.selected =self.item.name
        #else:
        #    self.owner.selected = self.item.name2()


    # def on_release(self):
    #     if self.type == 'Countries' or self.type == 'Country' or self.type == 'Province' or self.type == 'Locality' or self.type == 'Place' or self.type == 'TreeViewItemDaysOfPhotosWithoutPlace':
    #         print(self.owner)
    #         photoListRecyclerView = self.owner.ids['screenDatabase']
    #         print(photoListRecyclerView.data)
    #         photoListRecyclerView.accept(self.data)
    #         return
    #
    #     if self.expandable:
    #         if self.type == 'Album':
    #             self.owner.expanded_albums = not self.owner.expanded_albums
    #         elif self.type == 'Tag':
    #             self.owner.expanded_tags = not self.owner.expanded_tags
    #         elif self.type == 'Person':
    #             self.owner.expanded_persons = not self.owner.expanded_persons
    #         elif self.type == 'Folder':
    #             self.owner.expanded_folders = not self.owner.expanded_folders
    #         elif self.type == "Countries":
    #             self.owner.expanded_countries = not self.owner.expanded_countries
    #         elif self.type == "Country":
    #             self.owner.expanded_country = not self.owner.expanded_country
    #
    #    # self.owner.update_treeview()

    def on_touch_move(self, touch):
        if self.drag:
            delay = time.time() - touch.time_start
            if delay >= drag_delay:
                app = App.get_running_app()
                window_coords = self.to_window(touch.pos[0], touch.pos[1])
                app.drag_treeview(self, 'move', window_coords)

    def on_touch_up(self, touch):
      #  if self.collide_point(*touch.pos) and self.collide_point(*touch.opos):
       #     self.on_release()

        if self.drag:
            app = App.get_running_app()
            window_coords = self.to_window(touch.pos[0], touch.pos[1])
            app.drag_treeview(self, 'end', window_coords)
            self.drag = False