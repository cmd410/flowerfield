import json
from weakref import ref
from typing import Mapping, Sequence, List
from collections import abc


class SchemaError(RuntimeError):
    pass


class FieldTypeError(SchemaError):
    pass


class Field:

    __slots__ = (
        'type', 'name', 'is_struct', 'owner'
    )

    def __init__(self, type=None):
        self.type = type
        if isinstance(type, tuple):
            self.is_struct = any([issubclass(i, Scheme) for i in type])
        else:
            self.is_struct = issubclass(type, Scheme)
        self.name = None

    def get_value(self, obj):
        return obj.__dict__.get(f'_field_{self.name}')

    def set_value(self, obj, value):
        obj.__dict__[f'_field_{self.name}'] = value

    def get_struct(self, value):
        if issubclass(self.type, Scheme):
            return self.type
        elif isinstance(self.type, tuple):
            struct_map = {}
            for i in self.type:
                if not issubclass(i, Scheme):
                    continue
                struct_map[i.coverage(set(value.keys()))] = i
            return struct_map[max(struct_map.keys())]

    def __get__(self, obj, cls=None):
        if obj is None:
            return
        return self.get_value(obj)

    def __set__(self, obj, value):
        if obj is None:
            return
        if self.type is None:
            self.set_value(obj, value)
        elif isinstance(value, self.type):
            self.set_value(obj, value)
        elif isinstance(value, Mapping) and self.is_struct:
            self.set_value(obj, self.get_struct(value).from_dict(value))
        else:
            raise FieldTypeError(
                f'Wrong type {type(value)} for field:\n{repr(self)}\n'
                f'Scheme: {self.owner()}\n'
                f'Given value: {repr(value)}'
                )

    def __set_name__(self, owner, name):
        self.name = name
        self.owner = ref(owner)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(name={self.name}, type={self.type})'


class ListField(Field):
    def unpack_list(self, in_list: list):
        new_list = []
        for value in in_list:
            if isinstance(value, self.type):
                new_list.append(value)
            elif isinstance(value, Mapping) and self.is_struct:
                new_list.append(self.get_struct(value).from_dict(value))
            elif isinstance(value, list):
                new_list.append(self.unpack_list(value))
            else:
                raise FieldTypeError(
                    f'Wrong type {type(value)} for field:\n{repr(self)}'
                    )
        return new_list

    def __set__(self, obj, value_list):
        if value_list is None:
            self.set_value(obj, None)
            return
        assert(isinstance(value_list, list))
        self.set_value(obj, self.unpack_list(value_list))


class Scheme(abc.Mapping):

    _fields = frozenset()
    _root = True

    def __init_subclass__(cls, /, root=False, **kwargs):
        super().__init_subclass__(**kwargs)
        _fields = set()
        for name, value in cls.__dict__.items():
            if isinstance(value, Field):
                _fields.add(name)
        cls._fields = frozenset(_fields)
        cls._root = root

    @classmethod
    def from_dict(cls, d: Mapping) -> 'Scheme':
        assert(isinstance(d, Mapping))

        coverage = None

        if cls._root:
            struct_map = {}
            for i in cls.__subclasses__():
                struct_map[i.coverage(set(d.keys()))] = i
            coverage = max(struct_map.keys())
            cls = struct_map[coverage]

        if coverage is None:
            coverage = cls.coverage(set(d.keys()))

        if not coverage:
            raise SchemaError(
                'Cannot map structure none of the fields match!\n'
                f'Scheme: {cls.__qualname__}\n'
                f'Fields: {cls._fields}\n'
                f'Given mapping: {d}'
                )

        struct = cls()
        for field in cls._fields:
            struct[field] = d.get(field)
        return struct

    @classmethod
    def from_list(cls, in_list: Sequence) -> List['Scheme']:
        sl = []
        for i in in_list:
            sl.append(cls.from_dict(i))
        return sl

    @classmethod
    def coverage(cls, keys: set) -> int:
        return len(cls._fields.intersection(keys))

    def json_dumps(self, **kwargs) -> str:
        return json.dumps(self.as_dict(), **kwargs)

    def json_dump(self, fp, **kwargs):
        return json.dump(self.as_dict(), fp, **kwargs)

    @classmethod
    def json_loads(cls, json_string: str) -> 'Scheme':
        data = json.loads(json_string)
        if isinstance(data, dict):
            return cls.from_dict(data)
        elif isinstance(data, list):
            return cls.from_list(data)
        else:
            raise SchemaError(f'Cannot create Strucutre from {repr(data)}')

    def as_dict(self):
        d = {}
        for key in self._fields:
            value = getattr(self, key)
            if isinstance(value, Scheme):
                value = value.as_dict()
            d[key] = value
        return d

    def __repr__(self):
        s = f'{self.__class__.__name__}('
        s += ', '.join(
            [
                f'{field}={repr(getattr(self, field))}'
                for field in self._fields
            ]
        )
        return s + ')'

    def __getitem__(self, key):
        if key not in self._fields:
            raise KeyError(f'{self.__class__.__name__} has no field \"{key}\"')
        return getattr(self, key)

    def __setitem__(self, key, value):
        if key not in self._fields:
            raise KeyError(f'{self.__class__.__name__} has no field \"{key}\"')
        return setattr(self, key, value)

    def __iter__(self):
        for i in self._fields:
            yield i

    def __len__(self):
        return len(self._fields)

    def __contains__(self, key):
        return key in self._fields

    def keys(self):
        return self._fields

    def items(self):
        return [(key, getattr(self, key)) for key in self._fields]

    def values(self):
        return [getattr(key) for key in self._fields]

    def get(self, key, default=None):
        return getattr(self, key) if key in self._fields else default

    def __eq__(self, other):
        if not isinstance(other, Mapping):
            return False

        for key in self:
            if key not in other:
                return False
            else:
                if other[key] != self[key]:
                    return False
        return True

    def __ne__(self, other):
        return not (self == other)
