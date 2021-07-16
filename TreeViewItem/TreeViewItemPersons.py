from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemPerson import TreeViewItemPerson

class TreeViewItemPersons(TreeViewItem):
    indent = 0

    def visit(self, treeViewItem):
        super(TreeViewItemPersons, self).visit()

        if self.expanded:
            treeViewItem.data = self.deleteChild(treeViewItem.data, self)
            self.expanded = False
        else:
            index = self.getItemIndex(treeViewItem.data, self)
            for person in self.item.all():
                index += 1
                person_item = TreeViewItemPerson(self.owner, person, self.height, self)
                treeViewItem.data.insert(index, person_item)
            self.expanded = True