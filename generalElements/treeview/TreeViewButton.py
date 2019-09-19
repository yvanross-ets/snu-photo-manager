import time

from kivy.app import App
from kivy.properties import BooleanProperty, StringProperty, NumericProperty, ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.treeview import TreeViewNode

from generalconstants import drag_delay

from kivy.lang.builder import Builder

Builder.load_string("""

<TreeViewButton>:
    color_selected: app.theme.selected
    odd_color: app.list_background_odd
    even_color: app.list_background_even
    orientation: 'vertical'
    size_hint_y: None
    height: app.button_scale
    NormalLabel:
        mipmap: True
        markup: True
        text_size: (self.width - 20, None)
        halign: 'left'
        text: root.folder_name + '   [b]' + root.total_photos + '[/b]'
    NormalLabel:
        mipmap: True
        id: subtext
        text_size: (self.width - 20, None)
        font_size: app.text_scale
        color: .66, .66, .66, 1
        halign: 'left'
        size_hint_y: None
        height: 0
        text: root.subtext
    """)

class TreeViewButton(ButtonBehavior, BoxLayout, TreeViewNode):
    """Widget that displays a specific folder, album, or tag in the screenDatabase treeview.
    Responds to clicks and double-clicks.
    """

    displayable = BooleanProperty(True)
    target = StringProperty()  #Folder, Album, or Tag
    fullpath = StringProperty()  #Folder name, used only on folder type targets
    folder = StringProperty()
    database_folder = StringProperty()
    type = StringProperty()  #The type the target is: folder, album, tag, extra
    total_photos = StringProperty()
    folder_name = StringProperty()
    subtext = StringProperty()
    total_photos_numeric = NumericProperty(0)
    view_album = BooleanProperty(True)
    drag = False
    dragable = BooleanProperty(False)
    owner = ObjectProperty()
    droptype = StringProperty('folder')

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.is_double_tap:
                if self.view_album:
                    if self.total_photos_numeric > 0:
                        app = App.get_running_app()
                        if not app.shift_pressed:
                            app.show_album(self)
            else:
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
        self.owner.selected = ''
        self.owner.selected = self.target

    def on_release(self):
        if self.dragable:
            try:
                self.parent.toggle_node(self)
            except:
                pass

    def on_touch_move(self, touch):
        if self.drag:
            delay = time.time() - touch.time_start
            if delay >= drag_delay:
                app = App.get_running_app()
                window_coords = self.to_window(touch.pos[0], touch.pos[1])
                app.drag_treeview(self, 'move', window_coords)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.on_release()
        if self.drag:
            app = App.get_running_app()
            window_coords = self.to_window(touch.pos[0], touch.pos[1])
            app.drag_treeview(self, 'end', window_coords)
            self.drag = False