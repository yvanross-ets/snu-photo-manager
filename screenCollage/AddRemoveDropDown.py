from kivy.properties import ObjectProperty

from generalElements.dropDowns.NormalDropDown import NormalDropDown

from kivy.lang.builder import Builder

Builder.load_string("""
<AddRemoveDropDown>:
    MenuButton:
        text: '  Add All  '
        on_release: 
            root.owner.add_all()
            root.dismiss()
    MenuButton:
        text: '  Remove Selected  '
        warn: True
        on_release: 
            root.owner.delete_selected()
            root.dismiss()
    MenuButton:
        text: '  Clear All  '
        warn: True
        on_release: 
            root.owner.clear_collage()
            root.dismiss()
""")

class AddRemoveDropDown(NormalDropDown):
    owner = ObjectProperty()