from TreeViewItem.TreeViewItem import TreeViewItem


class TreeViewItemPlace(TreeViewItem):
    indent = 4
    dragable = True
    can_rename_folder = True
    can_delete_folder = True


    def __init__(self,owner,item, height, parent):
        self.owner = owner
        self.target = item.name2()
        self.item = item
        self.height = height
        self.treeViewItemParent = parent

    def visit(self, visitor):
        super(TreeViewItemPlace, self).visit()

        screenDatabase = self.owner
        datas = []
        for photo in self.item.photos:
            datas.append(photo.data_item(screenDatabase))

        screenDatabase.data = datas
        screenDatabase.update_can_browse()
        screenDatabase.update_selected()


    def visit_drop(self,visitors):
       self.item.add_photos(visitors)