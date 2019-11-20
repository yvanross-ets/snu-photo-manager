from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemDayOfPhotosWithoutPlace import TreeViewItemDayOfPhotosWithoutPlace
from models.DayOfPhotosWithoutPlace import DayOfPhotosWithoutPlace

class TreeViewItemDaysOfPhotosWithoutPlace(TreeViewItem):
    type = 'TreeViewItemDaysOfPhotosWithoutPlace'
    indent = 0

    def __init__(self, owner, item, height, parent=None):
        self.target = item.name
        self.owner = owner
        self.item = item
        self.height = height
        self.parent = parent

    def visit(self,visitor):
        if self.expanded:
            visitor.data = self.deleteChild(visitor.data, self)
            self.expanded = False
        else:
            index = None
            for idx, data in enumerate(visitor.data):
                if data == self:
                    index = idx
                    break

            for day in self.item.daysWithNbPhotos():
                index += 1
                dayOfPhotoWithoutPlace = DayOfPhotosWithoutPlace(day[0],day[1],day[2])
                day_item = TreeViewItemDayOfPhotosWithoutPlace(self.owner, dayOfPhotoWithoutPlace, self.height, self)
                visitor.data.insert(index, day_item)
            self.expanded = True