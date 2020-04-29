from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemProvince import TreeViewItemProvince

class TreeViewItemCountry(TreeViewItem):
    indent = 1
    can_delete_folder = True

    def visit(self, visitor):
        super(TreeViewItemCountry, self).visit()

        if self.expanded:
          visitor.data = self.deleteChild(visitor.data, self)
          self.expanded = False
        else:
          index = self.getItemIndex(visitor.data,self)
          for province in self.item.provinces:
              index += 1
              country_item = TreeViewItemProvince(self.owner, province, self.height, self)
              visitor.data.insert(index, country_item)
          self.expanded = True


