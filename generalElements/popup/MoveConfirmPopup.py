from kivy.properties import StringProperty, ListProperty

from generalElements.NormalPopup import NormalPopup


class MoveConfirmPopup(NormalPopup):
    """Popup that asks to confirm a file or folder move."""
    target = StringProperty()
    photos = ListProperty()
    origin = StringProperty()