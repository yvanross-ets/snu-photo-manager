# import abc
# class ITreeViewItem(object):
#     __metaclass__ = abc.ABCMeta
#
#     @abc.abstractmethod
#     def test(self):
#         raise NotImplementedError('Must implement test method to use this base class')


class TreeViewItem:
    target = None
    item = None
    owner = None
    total_photos = ''


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

