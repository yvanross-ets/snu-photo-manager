from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemCountry import TreeViewItemCountry

class TreeViewItemCountries(TreeViewItem):
    indent = 0
    can_delete_folder = True
    dragable = True


    def visit(self,treeViewItem):
        super(TreeViewItemCountries, self).visit()

        if self.expanded:
            treeViewItem.data = self.deleteChild(treeViewItem.data, self)
            self.expanded = False
        else:
            index = self.getItemIndex(treeViewItem.data,self)
            try:
                for country in self.item.all():
                    index += 1
                    country_item = TreeViewItemCountry(self.owner, country, self.height, self)
                    treeViewItem.data.insert(index, country_item)
                self.expanded = True
            except:
                pass
