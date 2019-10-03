from TreeViewItem.TreeViewItem import TreeViewItem
from models.Tags import Tags

class TreeViewItemTags(TreeViewItem):
    #fullpath = 'Tags'
    #folder_name = 'Tags'
    target = 'Tags'
    type = 'Tag'
    #total_photos = ''
    displayable = True
    expandable = None
    item = Tags()
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

