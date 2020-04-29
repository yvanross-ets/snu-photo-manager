from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemPlace import TreeViewItemPlace
from TreeViewItem.TreeViewItemPlace import TreeViewItemPlace

class TreeViewItemLocality(TreeViewItem):
    indent = 3
    can_delete_folder = True

    def visit(self, visitor):
        super(TreeViewItemLocality, self).visit()

        if self.expanded:
          visitor.data = self.deleteChild(visitor.data, self)
          self.expanded = False
        else:
          index = self.getItemIndex(visitor.data,self)
          for places in self.item.places:
              index += 1
              country_item = TreeViewItemPlace(self.owner, places, self.height, self)
              visitor.data.insert(index, country_item)
          self.expanded = True


