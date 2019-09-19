from kivy.properties import ObjectProperty

from generalElements.NormalDropDown import NormalDropDown
from kivy.lang.builder import Builder

Builder.load_string("""


<ResolutionDropDown>:
    MenuButton:
        text: 'Medium'
        on_release: 
            root.owner.resolution = self.text
            root.dismiss()
    MenuButton:
        text: 'High'
        on_release: 
            root.owner.resolution = self.text
            root.dismiss()
    MenuButton:
        text: 'Low'
        on_release: 
            root.owner.resolution = self.text
            root.dismiss()
""")

class ResolutionDropDown(NormalDropDown):
    owner = ObjectProperty()