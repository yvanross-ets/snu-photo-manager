from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemCountry import TreeViewItemCountry

class TreeViewItemCountries(TreeViewItem):
    indent = 0
    can_delete_folder = True
    dragable = True


    def visit(self,visitor):
        super(TreeViewItemCountries, self).visit()

        if self.expanded:
            visitor.data = self.deleteChild(visitor.data, self)
            self.expanded = False
        else:
            index = self.getItemIndex(visitor.data,self)
            try:
                for country in self.item.all():
                    index += 1
                    country_item = TreeViewItemCountry(self.owner, country, self.height, self)
                    visitor.data.insert(index, country_item)
                self.expanded = True
            except:
                pass
