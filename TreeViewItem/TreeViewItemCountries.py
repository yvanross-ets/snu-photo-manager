from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemCountry import TreeViewItemCountry

class TreeViewItemCountries(TreeViewItem):
    type = 'Countries'
    indent = 0

    def __init__(self, owner, item, height, parent=None):
        self.target = item.name
        self.owner = owner
        self.item = item
        self.height = height
        self.parent = parent

    def visit(self,visitor):
        if self.expanded:
            visitor.data = self.deleteChild(visitor.data, self)
            self.expanded = False
        else:
            index = None
            for idx, data in enumerate(visitor.data):
                if data == self:
                    index = idx
                    break
            for country in self.item.countries():
                index += 1
                country_item = TreeViewItemCountry(self.owner, country, self.height, self)
                visitor.data.insert(index, country_item)
            self.expanded = True