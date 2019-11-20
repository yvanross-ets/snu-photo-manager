from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemPlace import TreeViewItemPlace
from TreeViewItem.TreeViewItemPlace import TreeViewItemPlace

class TreeViewItemLocality(TreeViewItem):
    type = 'Locality'
    indent = 2

    def __init__(self,owner,item, height, parent):
        self.owner = owner
        self.target = item.name
        self.item = item
        self.height = height
        self.treeViewItemParent = parent

    def visit(self, visitor):
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


