from TreeViewItem.TreeViewItem import TreeViewItem

class TreeViewItemTag(TreeViewItem):
    #fullpath = 'Tag'
    #folder_name = None
    #total_photos = None
    #total_photos_numeric = None
    #target = None
    type = 'Tag'
    expandable = False
    displayable = True
    #owner = None
    indent = 1
    subtext = ''
    end = False
    height = None
    dragable = False

    def __init__(self,owner,tag,height):
        self.owner = owner
        #self.folder_name = tag.name
        #self.total_photos_numeric = len(tag.photos)
        #self.total_photos = '('+str(self.total_photos_numeric)+')'
        self.target = tag.name
        self.height = height
        self.item = tag
