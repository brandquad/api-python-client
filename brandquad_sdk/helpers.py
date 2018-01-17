from collections import OrderedDict
from itertools import islice


class SlicableOrderedDict(OrderedDict):
    def __getitem__(self, k):
        if not isinstance(k, slice):
            return OrderedDict.__getitem__(self, k)
        return SlicableOrderedDict(islice(self.items(), k.start, k.stop))


def _wrap(method):
    def wrapper(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        self.callback()
        return result
    return wrapper


class AttributeDict(dict):
    __slots__ = ["callback"]

    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        dict.__init__(self, *args, **kwargs)

    __delitem__ = _wrap(dict.__delitem__)
    __setitem__ = _wrap(dict.__setitem__)
    clear = _wrap(dict.clear)
    pop = _wrap(dict.pop)
    popitem = _wrap(dict.popitem)
    setdefault = _wrap(dict.setdefault)
    update = _wrap(dict.update)
