from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemFace import TreeViewItemFace

class TreeViewItemFaces(TreeViewItem):
    indent = 0

    def visit(self,visitor):
        super(TreeViewItemFaces, self).visit()

        if self.expanded:
            visitor.data = self.deleteChild(visitor.data, self)
            self.expanded = False
        else:
            index = self.getItemIndex(visitor.data, self)
            for face in self.item.all():
                index += 1
                face_item = TreeViewItemFace(self.owner, face, self.height, self)
                visitor.data.insert(index, face_item)
            self.expanded = True