from kivy.app import App

class TreeViewItem:
    target = None    # name of the displayed text
    item = None
    owner = None
    treeViewItemParent = None
    indent = 0
    displayable = True
    expanded = False
    expandable = True
    dragable = False
    height = 50
    total_photos = ''
    end = True
    can_new_folder = False
    can_rename_folder = False
    can_delete_folder = False

    def __init__(self, owner, item, height, parent=None):
        self.owner = owner
        self.target = item.name
        self.item = item
        self.height = height
        self.treeViewItemParent = parent

    def dict(self):
        ret = {}
        for attr in dir(self):
            if not attr.startswith('__'):
                ret[attr] = getattr(self, attr)
        return ret

    def displayable_dict(self):
        ret =self.dict()
        ret['target'] = str(ret['target'])
        if hasattr(self,'id'):
            ret['id']=str(ret['id'])
        return ret

    def get(self, attr, default):
        value = None
        if hasattr(self, attr):
            value = getattr(self, attr)

        if value is None:
            value = default

        return value

    def deleteChild(self, observableList, treeViewItemParent):
        for idx, data in reversed(list(enumerate(observableList))):
            if hasattr(data, 'treeViewItemParent') and data.treeViewItemParent == treeViewItemParent:
                observableList.pop(idx)
                observableList = self.deleteChild(observableList, data)
        self.expanded = False
        return observableList

    def getItemIndex(self, list, item):
        index = None
        for idx, data in enumerate(list):
            if data == item:
                index = idx
                break
        return index

    def visit_drop(self,treeViewItem):
        app = App.get_running_app()
        app.popup_message("Dropping photos to " + self.target + " is not permitted", title='Warning')

    def visit(self):
        self.owner.on_selected(self)

    def visit_delete(self, treeViewItems):
        if self.item.can_delete():
            self.item.delete()
            treeViewItems.remove(self)