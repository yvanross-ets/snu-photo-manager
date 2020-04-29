from TreeViewItem.TreeViewItem import TreeViewItem

class TreeViewItemFace(TreeViewItem):
    indent = 1

    def visit(self,visitor):
        super(TreeViewItemFace, self).visit()

        if self.expanded:
            visitor.data = self.deleteChild(visitor.data, self)
            self.expanded = False
        else:
           raise Exception("TreeViewItemFace: Visit photos with faces")
