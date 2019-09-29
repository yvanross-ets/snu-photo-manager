from kivy.properties import NumericProperty, StringProperty

from generalElements.popups.NormalPopup import NormalPopup

from kivy.lang.builder import Builder

Builder.load_string("""

<ScanningPopup>:
    GridLayout:
        cols: 1
        NormalLabel:
            id: scanningText
            text: root.scanning_text
            text_size: self.size
        ProgressBar:
            id: scanningProgress
            value: root.scanning_percentage
            max: 100
        WideButton:
            id: scanningButton
            text: 'Cancel'
            """)
class ScanningPopup(NormalPopup):
    """Popup for displaying screenDatabase scanning progress."""
    scanning_percentage = NumericProperty(0)
    scanning_text = StringProperty('Building File List...')