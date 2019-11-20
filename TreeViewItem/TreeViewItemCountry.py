from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemProvince import TreeViewItemProvince

class TreeViewItemCountry(TreeViewItem):
    type = 'Country'
    indent = 1

    def __init__(self,owner,item, height, parent):
        self.owner = owner
        self.target = item.name
        self.name = "coco" #item.name
        self.item = item
        self.height = height
        self.treeViewItemParent = parent

    def visit(self, visitor):
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


