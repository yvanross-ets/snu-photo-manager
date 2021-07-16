from TreeViewItem.TreeViewItem import TreeViewItem

class TreeViewItemFace(TreeViewItem):
    indent = 1

    def visit(self,treeViewItem):
        super(TreeViewItemFace, self).visit()

        if self.expanded:
            treeViewItem.data = self.deleteChild(treeViewItem.data, self)
            self.expanded = False
        else:
           raise Exception("TreeViewItemFace: Visit photos with faces")
