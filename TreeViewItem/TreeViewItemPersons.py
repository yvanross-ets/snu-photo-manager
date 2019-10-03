from TreeViewItem.TreeViewItem import TreeViewItem

class Persons:
    photos = []
    pass

class TreeViewItemPersons(TreeViewItem):
    #fullpath = 'Persons'
    #folder_name = 'Persons'
    #target = 'Persons'
    type = 'Person'
    target = Persons()
    #total_photos = ''
    displayable = False
    expandable = None
    expanded = None
    #owner = None
    indent = 0
    subtext = ''
    height = None
    end = False
    dragable = False

    def __init__(self,owner,expandable, expanded, height):
        self.owner = owner
        self.expandable = expandable
        self.expanded = expanded
        self.height = height

