from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemLocality import TreeViewItemLocality

class TreeViewItemProvince(TreeViewItem):
    indent = 2
    can_delete_folder = True

    def visit(self,visitor):
        super(TreeViewItemProvince, self).visit()

        if self.expanded:
            visitor.data = self.deleteChild(visitor.data, self)
        else:
            index = self.getItemIndex(visitor.data, self)
            for locality in self.item.localities:
              index += 1
              country_item = TreeViewItemLocality(self.owner, locality, self.height, self)
              visitor.data.insert(index, country_item)
            self.expanded = True


