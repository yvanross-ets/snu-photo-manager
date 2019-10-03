from TreeViewItem.TreeViewItem import TreeViewItem

class TreeViewItemPerson(TreeViewItem):
    #fullpath = 'Person'
    #folder_name = None
    #total_photos = None
    #total_photos_numeric = None
    #target = None
    type = 'Person'
    expandable = False
    displayable = True
    #owner = None
    indent = 1
    subtext = ''
    end = False
    height = None
    dragable = False

    def __init__(self, owner, person, height):
        self.owner = owner
        self.height = height
        #self.folder_name = person.first_name + " " + person.last_name
        #self.total_photos_numeric = len(person.photos)
        #self.total_photos = '('+str(self.total_photos_numeric)+')' if self.total_photos_numeric > 0 else ''
        self.target = person.first_name + " " + person.last_name
        self.item = person
