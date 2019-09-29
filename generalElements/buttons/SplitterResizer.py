from kivy.uix.button import Button

from kivy.lang.builder import Builder

Builder.load_string("""

<SplitterResizer>:
    background_color: app.theme.sidebar_resizer
    background_normal: 'data/splitterbgup.png'
    background_down: 'data/splitterbgdown.png'
    border: 0, 0, 0, 0
    """)
class SplitterResizer(Button):
    pass