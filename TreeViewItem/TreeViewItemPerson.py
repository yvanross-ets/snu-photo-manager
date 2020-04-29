from TreeViewItem.TreeViewItem import TreeViewItem

class TreeViewItemPerson(TreeViewItem):
    indent = 1

    def visit(self, visitor):
        super(TreeViewItemPerson, self).visit()

        raise Exception("TreeViewItemPerson: Visit to implement")