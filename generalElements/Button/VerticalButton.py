from kivy.properties import StringProperty

from generalElements.Button.ToogleBase import ToggleBase

from kivy.lang.builder import Builder

Builder.load_string("""

<VerticalButton>:
    size_hint_y: None
    width: app.button_scale
    size_hint_x: None
    font_size: app.text_scale
    height: textArea.texture_size[0] + 100
    background_down: 'data/buttonright.png'
    Label:
        id: textArea
        center: self.parent.center
        canvas.before:
            PushMatrix
            Rotate:
                angle: 90
                axis: 0,0,1
                origin: self.center
        canvas.after:
            PopMatrix
        color: self.parent.color
        text: self.parent.vertical_text
""")
class VerticalButton(ToggleBase):
    vertical_text = StringProperty('')


#class VerticalButton(ToggleButton, ButtonBase):
#    pass
