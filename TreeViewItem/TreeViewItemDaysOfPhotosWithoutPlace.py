from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemDayOfPhotosWithoutPlace import TreeViewItemDayOfPhotosWithoutPlace
from models.DayOfPhotosWithoutPlace import DayOfPhotosWithoutPlace

class TreeViewItemDaysOfPhotosWithoutPlace(TreeViewItem):
    indent = 0

    def visit(self,visitor):
        super(TreeViewItemDaysOfPhotosWithoutPlace, self).visit()
        if self.expanded:
            visitor.data = self.deleteChild(visitor.data, self)
            self.expanded = False
        else:
            index = self.getItemIndex(visitor.data,self)
            for day in self.item.folders():
                index += 1
                dayOfPhotoWithoutPlace = DayOfPhotosWithoutPlace(day[0],day[1],day[2])
                day_item = TreeViewItemDayOfPhotosWithoutPlace(self.owner, dayOfPhotoWithoutPlace, self.height, self)
                visitor.data.insert(index, day_item)
            self.expanded = True