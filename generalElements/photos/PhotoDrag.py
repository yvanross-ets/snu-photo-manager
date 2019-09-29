from kivy.properties import NumericProperty, StringProperty
from kivy.uix.image import Image as KivyImage

from kivy.lang.builder import Builder

Builder.load_string("""

<PhotoDrag>:
    canvas.before:
        PushMatrix
        Rotate:
            angle: root.angle
            axis: 0,0,1
            origin: root.center
    canvas.after:
        PopMatrix

    height: (app.button_scale * 4)
    width: (app.button_scale * 4)
    size_hint_y: None
    size_hint_x: None
""")
class PhotoDrag(KivyImage):
    """Special image widget for displaying the drag-n-drop location."""

    angle = NumericProperty()
    offset = []
    opacity = .5
    fullpath = StringProperty()