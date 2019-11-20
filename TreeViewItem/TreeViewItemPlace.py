from TreeViewItem.TreeViewItem import TreeViewItem


class TreeViewItemPlace(TreeViewItem):
    type = 'Place'
    indent = 3

    def __init__(self,owner,item, height, parent):
        self.owner = owner
        self.target = item.name2()
        self.item = item
        self.height = height
        self.treeViewItemParent = parent

    def visit(self, visitor):
        screenDatabase = self.owner
        datas = []
        for photo in self.item.photos:
            datas.append(photo.data_item(screenDatabase))

        screenDatabase.data = datas
        screenDatabase.update_can_browse()
        screenDatabase.update_selected()

    #   if self.expanded:
     #       visitor.data = self.deleteChild(visitor.data, self)
      # else:
      #     index = self.getItemIndex(visitor.data,self)
      #     for province in self.item.provinces:
      #         index += 1
      #         country_item = TreeViewItemPlace(self.owner, province, self.height, self)
      #         visitor.data.insert(index, country_item)
      #     self.expanded = True


