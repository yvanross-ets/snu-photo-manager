import os
from kivy.app import App
from kivy.clock import Clock
from kivy.cache import Cache
from kivy.animation import Animation
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout

from functools import partial

from generalcommands import to_bool, get_folder_info, local_path
from generalElements.MenuButton import MenuButton
from generalElements.NormalDropDown import NormalDropDown
from generalElements.MoveConfirmPopup import MoveConfirmPopup
from generalElements.InputPopupTag import InputPopupTag
from generalElements.InputPopup import InputPopup
from generalElements.NormalPopup import NormalPopup
from generalElements.ConfirmPopup import ConfirmPopup
from generalElements.AlbumSortDropDown import AlbumSortDropDown
from generalconstants import *
from screenDatabase.databaseSortDropDown import DatabaseSortDropDown
from screenDatabase.folderDetails import FolderDetails

from kivy.lang.builder import Builder
import generalelements

Builder.load_string("""
<AlbumDetails>:
    size_hint_y: None
    height: app.button_scale if app.simple_interface else (app.button_scale * 2)
    orientation: 'horizontal'
    Header:
        height: app.button_scale if app.simple_interface else (app.button_scale * 2)
        ShortLabel:
            text: 'Description:'
        NormalInput:
            id: albumDescription
            height: app.button_scale if app.simple_interface else (app.button_scale * 2)
            input_filter: app.test_description
            multiline: True
            text: ''
            on_focus: app.new_description(self, root.owner)


""")


class AlbumDetails(BoxLayout):
    """Widget to display information about an album"""

    owner = ObjectProperty()
