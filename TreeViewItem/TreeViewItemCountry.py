from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemProvince import TreeViewItemProvince

class TreeViewItemCountry(TreeViewItem):
    indent = 1
    can_delete_folder = True

    def visit(self, treeViewItem):
        super(TreeViewItemCountry, self).visit()

        if self.expanded:
          treeViewItem.data = self.deleteChild(treeViewItem.data, self)
          self.expanded = False
        else:
          index = self.getItemIndex(treeViewItem.data,self)
          for province in self.item.provinces:
              index += 1
              country_item = TreeViewItemProvince(self.owner, province, self.height, self)
              treeViewItem.data.insert(index, country_item)
          self.expanded = True


