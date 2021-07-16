from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemFolder import TreeViewItemFolder

class TreeViewItemFolders(TreeViewItem):
    indent = 0

    def visit(self, treeViewItem):
        super(TreeViewItemFolders, self).visit()

        if self.expanded:
            treeViewItem.data = self.deleteChild(treeViewItem.data, self)
            self.expanded = False
        else:
            index = self.getItemIndex(treeViewItem.data, self)
            for folder in self.item.all():
                index += 1
                folder_item = TreeViewItemFolder(self.owner, folder, self.height, self)
                treeViewItem.data.insert(index, folder_item)
            self.expanded = True