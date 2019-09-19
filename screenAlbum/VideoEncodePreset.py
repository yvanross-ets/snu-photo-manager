from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from generalElements.MenuButton import MenuButton
from generalElements.NormalDropDown import NormalDropDown

from kivy.lang.builder import Builder

Builder.load_string("""
<VideoEncodePreset>:
    orientation: 'vertical'
    size_hint_y: None
    height: int(app.button_scale * 2.5)
    BoxLayout:
        orientation: 'vertical'
        LeftNormalLabel:
            text: 'Video Encode:'
        MenuStarterButton:
            text: root.preset_name
            size_hint_x: 1
            on_release: root.preset_drop.open(self)
    MediumBufferY:
""")

class VideoEncodePreset(BoxLayout):
    preset_drop = ObjectProperty()
    preset_name = StringProperty()

    def __init__(self, **kwargs):
        self.preset_drop = NormalDropDown()
        app = App.get_running_app()
        for index, preset in enumerate(app.encoding_presets):
            menu_button = MenuButton(text=preset['name'])
            menu_button.bind(on_release=self.set_preset)
            self.preset_drop.add_widget(menu_button)
        if app.selected_encoder_preset:
            self.preset_name = app.selected_encoder_preset
        else:
            self.preset_name = app.encoding_presets[0]['name']
        super(VideoEncodePreset, self).__init__(**kwargs)

    def set_preset(self, instance):
        app = App.get_running_app()
        self.preset_name = instance.text
        self.preset_drop.dismiss()
        app.selected_encoder_preset = self.preset_name