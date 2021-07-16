from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemFace import TreeViewItemFace

class TreeViewItemFaces(TreeViewItem):
    indent = 0

    def visit(self,treeViewItem):
        super(TreeViewItemFaces, self).visit()

        if self.expanded:
            treeViewItem.data = self.deleteChild(treeViewItem.data, self)
            self.expanded = False
        else:
            index = self.getItemIndex(treeViewItem.data, self)
            for face in self.item.all():
                index += 1
                face_item = TreeViewItemFace(self.owner, face, self.height, self)
                treeViewItem.data.insert(index, face_item)
            self.expanded = True