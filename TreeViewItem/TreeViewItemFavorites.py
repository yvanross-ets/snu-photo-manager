from TreeViewItem.TreeViewItem import TreeViewItem

class TreeViewItemFavorites(TreeViewItem):
    #fullpath = 'Favorites'
    type = 'Tag'
    #folder_name = None
    #total_photos_numeric = None
    #total_photos = None
    expandable = False
    displayable = True
    indent = 0
    subtext = ''
    height = None
    end = True
    dragable = False


    def __init__(self,owner,tag,height):
        self.owner = owner
        self.target = tag.name
        self.item = tag
        self.height = height

