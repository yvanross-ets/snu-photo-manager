from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemFolder import TreeViewItemFolder

class TreeViewItemFolders(TreeViewItem):
    indent = 0

    def visit(self, visitor):
        super(TreeViewItemFolders, self).visit()

        if self.expanded:
            visitor.data = self.deleteChild(visitor.data, self)
            self.expanded = False
        else:
            index = self.getItemIndex(visitor.data, self)
            for folder in self.item.all():
                index += 1
                folder_item = TreeViewItemFolder(self.owner, folder, self.height, self)
                visitor.data.insert(index, folder_item)
            self.expanded = True