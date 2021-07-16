import os
from TreeViewItem.TreeViewItem import TreeViewItem

class TreeViewItemFolder(TreeViewItem):
    indent = 1
    dragable = True

    def visit(self, treeViewItem):
        super(TreeViewItemFolder, self).visit()

        screenDatabase = self.owner
        datas = []
        for photo in self.item.photos:
            datas.append(photo.data_item(screenDatabase))

        screenDatabase.data = datas
        screenDatabase.update_can_browse()
        screenDatabase.update_selected()


