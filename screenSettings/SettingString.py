from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.settings import SettingItem

from generalElements.popups.InputPopup import InputPopup
from generalElements.popups.NormalPopup import NormalPopup
from kivy.lang.builder import Builder

Builder.load_string("""
<SettingString>:
    size_hint_y: None
    NormalButton:
        text: root.value or ''
        pos: root.pos
        font_size: '15sp'
        color: app.theme.text
""")

class SettingString(SettingItem):
    popup = ObjectProperty(None, allownone=True)
    textinput = ObjectProperty(None)

    def on_panel(self, instance, value):
        if value is None:
            return
        self.fbind('on_release', self._create_popup)

    def dismiss(self, *largs):
        if self.popup:
            self.popup.dismiss()
        app = App.get_running_app()
        if app.popup:
            app.popup = None
        self.popup = None

    def _validate(self, instance, answer):
        value = self.popup.content.ids['input'].text.strip()
        self.dismiss()
        if answer == 'yes':
            self.value = value

    def _create_popup(self, instance):
        content = InputPopup(text='', input_text=self.value)
        app = App.get_running_app()
        content.bind(on_answer=self._validate)
        self.popup = NormalPopup(title=self.title, content=content, size_hint=(None, None), size=(app.popup_x, app.button_scale * 5), auto_dismiss=True)
        app = App.get_running_app()
        app.popup = self.popup
        self.popup.open()