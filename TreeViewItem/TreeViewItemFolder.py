import os
from TreeViewItem.TreeViewItem import TreeViewItem

class TreeViewItemFolder(TreeViewItem):
    #fullpath = 'Folder'
    #id = None
    #folder_name = None
    #total_photos =None
    #total_photos_numeric = None
    #target = None
    #owner = None
    type = 'Folder'
    expandable = False
    displayable = True
    #owner = None
    indent = 1
    subtext = ''
    end = False
    height = None
    dragable = False
    name='XXXXX'
    fullpath='XXXXX'

    def __init__(self,owner,folder, height, expandable=False, expanded=False):
        self.owner = owner
        self.target = folder.name
        self.item = folder
        #self.id = folder.id
        #self.folder_name = folder.path
        #self.total_photos_numeric = len(folder.photos)
        #self.total_photos = '('+str(self.total_photos_numeric)+')' if self.total_photos_numeric > 0 else ''
        self.height = height
        self.expandable = expandable
        self.expanded = expanded
        self.name = owner.name
        self.fullpath='y1234'



    def visit(self, visitor):
        screenDatabase = self.owner
        datas = []
        for photo in self.item.photos:
            datas.append(photo.data_item(screenDatabase))

        screenDatabase.data = datas
        screenDatabase.update_can_browse()
        screenDatabase.update_selected()


