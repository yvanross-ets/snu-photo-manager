from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemPerson import TreeViewItemPerson

class TreeViewItemPersons(TreeViewItem):
    indent = 0

    def visit(self, visitor):
        super(TreeViewItemPersons, self).visit()

        if self.expanded:
            visitor.data = self.deleteChild(visitor.data, self)
            self.expanded = False
        else:
            index = self.getItemIndex(visitor.data, self)
            for person in self.item.all():
                index += 1
                person_item = TreeViewItemPerson(self.owner, person, self.height, self)
                visitor.data.insert(index, person_item)
            self.expanded = True