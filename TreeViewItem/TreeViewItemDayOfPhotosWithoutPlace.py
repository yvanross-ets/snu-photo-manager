from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemProvince import TreeViewItemProvince

class TreeViewItemDayOfPhotosWithoutPlace(TreeViewItem):
    type = 'Country'
    indent = 1

    def __init__(self,owner,item, height, parent):
        self.owner = owner
        self.target = item.name
        self.name = "coco" #item.name
        self.item = item
        self.height = height
        self.treeViewItemParent = parent

    def visit(self, visitor):
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


