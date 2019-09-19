from kivy.uix.settings import SettingItem

from kivy.lang.builder import Builder

Builder.load_string("""
<SettingAboutButton>:
    WideButton:
        text: "About Snu Photo Manager"
        size: root.size
        pos: root.pos
        font_size: '15sp'
        on_release: app.about()
""")

class SettingAboutButton(SettingItem):
    """Widget that opens an about dialog."""
    pass