from enum import Enum

CLASS_SPECS_CACHE = dict()
TYPE_FIELD_NAME_FIELD_NAME = '_type_field_name'
TYPE_FIELD_NAME_FIELD_POSITION = '_type_field_position'
TYPE_FIELD_NAME_FIELD_ROOT = '_type_field_root'
TYPE_AS_LIST = '_type_as_list'
BUILTIN_TYPES = {
    int, float, str, type(None), bool, list, dict
}


class Position(Enum):
    INSIDE = 0
    OUTSIDE = 1


class PyjacksonError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return '{}'.format(self.msg)


class Unserializable:
    pass
