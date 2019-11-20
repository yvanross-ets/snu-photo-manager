# import abc
# class ITreeViewItem(object):
#     __metaclass__ = abc.ABCMeta
#
#     @abc.abstractmethod
#     def test(self):
#         raise NotImplementedError('Must implement test method to use this base class')


class TreeViewItem:
    target = None    # name of the displayed text
    item = None
    owner = None
    treeViewItemParent = None
    type = None
    indent = 0
    displayable = True
    expanded = False
    expandable = True
    dragable = False
    height = 50
    total_photos = ''
    end = True

    def __init__(self, owner, item, type, parent=None):
        self.item = item
        self.type = type
        self.owner = owner
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