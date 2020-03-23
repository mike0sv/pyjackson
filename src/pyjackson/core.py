import inspect
import typing
from enum import Enum

CLASS_SPECS_CACHE = dict()
TYPE_FIELD_NAME_FIELD_NAME = '_type_field_name'
TYPE_FIELD_NAME_FIELD_POSITION = '_type_field_position'
TYPE_FIELD_NAME_FIELD_ROOT = '_type_field_root'
FIELD_MAPPING_NAME_FIELD = '_field_mapping'
TYPE_AS_LIST = '_type_as_list'
BUILTIN_TYPES = {
    int, float, str, type(None), bool, list, dict
}
SERIALIZABLE_DICT_TYPES = {
    str, int, float
}


class Position(Enum):
    """Enum to change field with type information position
    """
    INSIDE = 0
    OUTSIDE = 1


class Unserializable:
    """Mixin type to signal that type is not serializable.
     :func:`pyjackson.serialize` will throw explicit error if called with instance of Unserializable
     (or object with nested Unserializable)"""
    pass


class Comparable:
    def __eq__(self, other):
        cls = type(self)
        if cls != type(other):
            return False

        args = inspect.getfullargspec(cls.__init__).args[1:]
        for a in args:
            if getattr(self, a) != getattr(other, a):
                return False
        return True


class Field(Comparable):
    def __init__(self, name: str, type: type, has_default: bool, default: typing.Any = None):
        self.name = name
        self.type = type
        self.has_default = has_default
        self.default = default

    def __str__(self):
        if self.has_default:
            return f'{self.name}: {self.type.__name__} = {self.default}'
        return f'{self.name}: {self.type.__name__}'

    def __repr__(self):
        return str(self)


ArgList = typing.List[Field]
Signature = typing.NamedTuple('Signature', [('args', ArgList), ('output', Field)])
