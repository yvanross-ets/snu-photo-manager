from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemProvince import TreeViewItemProvince

class TreeViewItemDayOfPhotosWithoutPlace(TreeViewItem):
    indent = 1

    def visit(self, visitor):
        super(TreeViewItemDayOfPhotosWithoutPlace, self).visit()
        screenDatabase = self.owner
        datas = []
        for photo in self.item.photos():
            if photo.longitude is None:
                print(photo)
                data_item = photo.data_item(screenDatabase)
                datas.append(data_item)

        screenDatabase.data = datas
        screenDatabase.update_can_browse()
        screenDatabase.update_selected()


