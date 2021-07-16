from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemLocality import TreeViewItemLocality

class TreeViewItemProvince(TreeViewItem):
    indent = 2
    can_delete_folder = True

    def visit(self,treeViewItem):
        super(TreeViewItemProvince, self).visit()

        if self.expanded:
            treeViewItem.data = self.deleteChild(treeViewItem.data, self)
        else:
            index = self.getItemIndex(treeViewItem.data, self)
            for locality in self.item.localities:
              index += 1
              country_item = TreeViewItemLocality(self.owner, locality, self.height, self)
              treeViewItem.data.insert(index, country_item)
            self.expanded = True


