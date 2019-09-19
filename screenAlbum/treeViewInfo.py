try:
    import numpy
    import cv2
    opencv = True
except:
    opencv = False
from PIL import  ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from kivy.config import Config
Config.window_icon = "data/icon.png"
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.treeview import TreeViewNode
from kivy.lang.builder import Builder

Builder.load_string("""
<TreeViewInfo>:
    color_selected: app.selected_color
    odd_color: app.list_background_odd
    even_color: app.list_background_even
    size_hint_y: None
    height: app.button_scale
    orientation: 'horizontal'
    LeftNormalLabel:
        text: root.title

""")



class TreeViewInfo(BoxLayout, TreeViewNode):
    """Simple treeview node to display a line of text.
    Has two elements, they will be shown as: 'title: content'"""

    title = StringProperty()
