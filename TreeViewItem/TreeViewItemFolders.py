from TreeViewItem.TreeViewItem import TreeViewItem
from models.Folders import Folders

class TreeViewItemFolders(TreeViewItem):
    #fullpath = 'Folders'
    #folder_name = 'Folders'
    target = 'Folders'
    item = Folders()
    type = 'Folder'
    #total_photos = ''
    displayable = True
    expandable = True
    expanded = None
    #owner = None
    indent = 0
    subtext = ''
    height = None
    end = False
    dragable = False


    def __init__(self, owner, expanded, height):
        self.expanded = expanded
        self.height = height
        self.owner = owner

