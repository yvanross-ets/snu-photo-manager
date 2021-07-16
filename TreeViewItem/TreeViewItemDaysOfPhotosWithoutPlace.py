from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemDayOfPhotosWithoutPlace import TreeViewItemDayOfPhotosWithoutPlace
from models.DayOfPhotosWithoutPlace import DayOfPhotosWithoutPlace

class TreeViewItemDaysOfPhotosWithoutPlace(TreeViewItem):
    indent = 0

    def visit(self,treeViewItem):
        super(TreeViewItemDaysOfPhotosWithoutPlace, self).visit()
        if self.expanded:
            treeViewItem.data = self.deleteChild(treeViewItem.data, self)
            self.expanded = False
        else:
            index = self.getItemIndex(treeViewItem.data,self)
            for day in self.item.folders():
                index += 1
                dayOfPhotoWithoutPlace = DayOfPhotosWithoutPlace(day[0],day[1],day[2])
                day_item = TreeViewItemDayOfPhotosWithoutPlace(self.owner, dayOfPhotoWithoutPlace, self.height, self)
                treeViewItem.data.insert(index, day_item)
            self.expanded = True