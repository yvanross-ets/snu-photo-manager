from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemLocality import TreeViewItemLocality

class TreeViewItemProvince(TreeViewItem):
    type = 'Province'
    indent = 2

    def __init__(self,owner,item, height, parent):
        self.owner = owner
        self.target = item.name
        self.item = item
        self.height = height
        self.treeViewItemParent = parent


    def visit(self,visitor):
        if self.expanded:
            visitor.data = self.deleteChild(visitor.data, self)
        else:
            index = self.getItemIndex(visitor.data, self)
            for locality in self.item.localities:
              index += 1
              country_item = TreeViewItemLocality(self.owner, locality, self.height, self)
              visitor.data.insert(index, country_item)
            self.expanded = True


