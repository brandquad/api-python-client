import json
import requests

from .helpers import AttributeDict, SlicableOrderedDict


class Entity(object):
    def __init__(self, data=None, name=None, entry_point=None):
        self._data = data
        self._name = name
        self._entry_point = entry_point
        self._path = entry_point._path
        self._api = entry_point._api
        self._attributes = []
        self.help_fields = {}
        self.error = None

        self._name_mapping = {'File': ['links'],
                              'Folder': ['files'],
                              'Product': ['categories', 'relations', 'assets', 'set']}

        self.initial()

        super(Entity, self).__init__()
        self.changed = False

    def initial(self):
        if self._data is None:
            self.options()
            try:
                self._attributes = list(filter(lambda x: self.help_fields[x]['read_only'] is False, self.help_fields))
            except TypeError:
                pass
        else:
            self._attributes = self._data.keys()

        for attr in self._attributes:
            if attr == 'attributes':
                self._data[attr] = AttributeDict(self._change, self._data[attr])
            setattr(self, attr, self._data[attr] if self._data else None)
            if attr == 'meta':
                setattr(self, 'id', self._data[attr]['id'])

        if self._name and self._name_mapping.get(self._name):
            for attr in self._name_mapping[self._name]:
                initial_attr = None
                if hasattr(self, attr):
                    initial_attr = getattr(self, attr)
                    delattr(self, attr)

                setattr(self, attr, EntryPointFactory(self._entry_point._api,
                                                      '{}%s/{}/'.format(self._entry_point._path, attr),
                                                      initial_data=initial_attr,
                                                      entity_pk=self.id))

    def __str__(self):
        obj_id = self.id if hasattr(self, 'id') else self.meta['id'] if hasattr(self, 'meta') else None
        string = '<{} {}>'.format(self._name, obj_id) if obj_id else '<{} new>'.format(self._name)
        return string

    def __name__(self):
        return self._name

    def _change(self):
        self.changed = True

    def __setattr__(self, key, value):
        if hasattr(self, '_attributes') and hasattr(self, 'changed'):
            if not self.changed and key in self._attributes:
                self._change()
        super(Entity, self).__setattr__(key, value)

    def _collect_data(self):
        for attr in self._attributes:
            attr_data = getattr(self, attr)
            if self._data is None:
                self._data = {}
            if isinstance(attr_data, Entity):
                attr_data = attr_data.id if hasattr(attr_data, 'id') else attr_data.meta['id']
            self._data.update({attr: attr_data})
        return self._data

    def save(self):
        data = self._collect_data()

        if self._name == 'Product':
            data = self.attributes
            data = {'data': json.dumps(data)}

        if hasattr(self, 'id'):
            response = self._api.get_response(requests.post, data=data, path=self._path)
        else:
            response = self._api.get_response(requests.post, data=data, path=self._path)

        status = int(response.status_code/100)
        _data = json.loads(response.text)
        if status != 4:
            self._data = _data[0] if isinstance(_data, list) else _data
        else:
            self.error = _data

        self.initial()
        self._entry_point._update_object(self)
        return self

    def delete(self, leave_in_cache=False):
        if hasattr(self, 'id'):
            self._api.get_response(requests.delete, path=self._path, pk=self.id)
            if not leave_in_cache:
                self._entry_point.items.pop(self.id)

    def options(self):
        text = self._api.get_response(requests.options, path=self._path).text
        self.help_fields = json.loads(text)['actions']['POST']

        return self.help_fields

    __repr__ = __str__


class EntryPointFactory(object):
    def __init__(self, api, path, initial_data=None, entity_pk=None):
        entity_mapping = {'attributes/': ('Attribute', 'Attributes'),
                          'attributes/types/': ('Type', 'Types'),
                          'attributes/groups/': ('Group', 'Groups'),
                          'categories/': ('Category', 'Categories'),
                          'dam/files/': ('File', 'Files'),
                          'dam/folders/': ('Folder', 'Folders'),
                          'dam/folders/%s/files/': ('File', 'Files'),
                          'products/': ('Product', 'Products'),
                          'dam/files/%s/links/': ('FileLink', 'FileLinks'),
                          'products/%s/categories/': ('ProductCategory', 'ProductCategories'),
                          'products/%s/relations/': ('ProductRelation', 'ProductRelations'),
                          'products/%s/assets/': ('ProductAsset', 'ProductAssets'),
                          'products/%s/set/': ('Set', 'ProductsSet')}

        self._api = api
        self._path = path
        self._entity = entity_mapping[path][0]
        self._name = entity_mapping[path][1]

        if self._name == 'Attributes':
            for attr in ['types', 'groups']:
                path = '{}{}/'.format(self._path, attr)
                setattr(self, attr, EntryPointFactory(self._api, path))

        if entity_pk:
            self._path = self._path % entity_pk

        self._next = None
        self._prev = None

        self.count = None
        self.items = SlicableOrderedDict()
        self.iter_scope = 0

        self._iter_items = None

        self.error = None
        self.maximum_items = None
        self._request_params = {}

        if initial_data:
            self._build_from_initial(initial_data)

    def __iterate(self):
        self.iter_scope = 0

        if self.count is None:
            self.__build_objects(self._api.get_response(requests.get, data=self._request_params, path=self._path).text)
        if self.count:
            for self.iter_scope in range(self.count):
                if self.maximum_items and self.iter_scope == self.maximum_items:
                    break
                if len(self.items) == self.iter_scope:
                    self.__build_objects(self._api.get_response(requests.get, fullurl=self._next).text)

    def _build_from_initial(self, initial_data):

        def _build(data):
            obj_id = data.get('id') if isinstance(data, dict) else None
            if obj_id:
                obj = Entity(data=data, name=self._entity, entry_point=self)
                return obj_id, obj
            return None, None

        if isinstance(initial_data, dict):
            obj_id, obj = _build(initial_data)
            self.items.update({obj_id: obj})
        else:
            for data in initial_data:
                obj_id, obj = _build(data)
                self.items.update({obj_id: obj})

    def _update_object(self, obj):
        if hasattr(obj, 'id'):
            self.items.update({obj.id: obj})
        else:
            self.error = ''

    def __build_objects(self, text):
        raw_data = json.loads(text)
        obj_id = None
        items = []
        if isinstance(raw_data, list) and len(raw_data) == 1:
            raw_data = raw_data[0]
        if 'results' in raw_data:
            self.count = raw_data['count']
            self._next = raw_data['next']
            self._prev = raw_data['previous']
            items = raw_data['results']
        elif 'meta' in raw_data:
            obj_id = raw_data['meta']['id']
        elif 'id' in raw_data:
            obj_id = raw_data['id']
        elif isinstance(raw_data, list) and len(raw_data) > 1:
            if 'id' in raw_data[0]:
                items = raw_data
        else:
            self.error = raw_data

        if obj_id:
            obj = Entity(data=raw_data, name=self._entity, entry_point=self)
            self.items.update({obj_id: obj})
        elif not self.error:
            if items:
                for item in items:
                    obj = Entity(data=item, name=self._entity, entry_point=self)
                    obj_id = obj.id if hasattr(obj, 'id') else obj.meta['id']
                    self.items.update({obj_id: obj})

    def get(self, pk=None, force=False):
        item = self.items.get(pk)

        if force or not item:
            self.__build_objects(self._api.get_response(requests.get, path=self._path, pk=pk).text)
            return self.items.get(pk)
        else:
            return item

    def list(self, force=False, maximum_items=None, **kwargs):
        self.maximum_items = maximum_items
        self._request_params = kwargs
        if force or not self.items:
            self.__iterate()

        self._request_params = {}
        max_items = self.maximum_items
        self.maximum_items = None
        return self.items[:max_items]

    def save(self):
        items_to_save = filter(lambda x: x.changed is True, self.items)
        for item in items_to_save:
            item.save()

    def delete(self):
        for item in self.items:
            item.delete()

    def new(self):
        return Entity(name=self._entity, entry_point=self)

    def clear_cache(self):
        self.items = SlicableOrderedDict()

    def __iter__(self):
        items = self.list()
        iterator = iter(self.items.__iter__())
        while True:
            if len(items) != len(self.items):
                iterator = iter(self.items[len(items):].__iter__())
                items = self.items
            if len(self.items) == self.count == self.maximum_items:
                break
            yield next(iterator)

    def __str__(self):
        return self._name

    __repr__ = __str__
