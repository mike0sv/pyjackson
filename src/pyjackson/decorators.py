import typing
from copy import copy

from pyjackson import utils
from pyjackson.core import (FIELD_MAPPING_NAME_FIELD, TYPE_AS_LIST, TYPE_FIELD_NAME_FIELD_NAME,
                            TYPE_FIELD_NAME_FIELD_POSITION, TYPE_FIELD_NAME_FIELD_ROOT, Position)
from pyjackson.generics import _register_serializer
from pyjackson.utils import get_class_field_names


class cached_property:
    def __init__(self, method):
        self.method = method
        self.field_name = '__{}_value'.format(method.__name__)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if not hasattr(instance, self.field_name):
            value = self.method(instance)
            setattr(instance, self.field_name, value)
        else:
            value = getattr(instance, self.field_name)
        return value


def make_string(*fields: str, include_name=True):
    """
    Decorator to create a `__str__` method for class based on `__init__` arguments

    Usage: directly :func:`@make_string` on class declaration to include all fields
    or :func:`@make_string(*fields, include_name)` to alter params

    :param fields: list of strings with field names
    :param include_name: whether to include class name
    """
    if len(fields) == 1 and not isinstance(fields[0], str):
        cls = fields[0]
        fields = []
    else:
        cls = None

    def make_str(cls):
        def __str__(self):
            flds = fields or [f.name for f in utils.get_function_fields(cls.__init__, False)]
            args = ','.join('{}={}'.format(key, getattr(self, key)) for key in flds)
            args_str = str(args)
            if include_name:
                args_str = '({})'.format(args_str)
            return cls.__name__ + args_str if include_name else args_str

        cls.__str__ = __str__
        cls.__repr__ = __str__
        return cls

    if cls is not None:
        return make_str(cls)
    return make_str


def as_list(cls: typing.Type):
    """
    Mark class to serialize it to list instead of dict

    :param cls: class to mark
    """
    setattr(cls, TYPE_AS_LIST, True)
    return cls


def type_field(field_name, position: Position = Position.INSIDE, allow_reregistration=False):
    """Class decorator for polymorphic hierarchies to define class field name, where subclass's type alias will be stored
    Use it on hierarchy root class, add class field  with defined name to any subclasses
    The same field name will be used during deserialization

    :param field_name: class field name to put alias for type
    :param position: where to put type alias
    :param allow_reregistration: whether to allow reregistration of same alias or throw error
    """

    class SubtypeRegisterMixin:
        _subtypes = dict()

        locals()[TYPE_FIELD_NAME_FIELD_NAME] = field_name
        locals()[TYPE_FIELD_NAME_FIELD_POSITION] = position

        def __init_subclass__(cls, **kwargs):
            super(SubtypeRegisterMixin, cls).__init_subclass__(**kwargs)
            subtype_name = cls.__dict__.get(field_name, f'{cls.__module__}.{cls.__name__}')
            setattr(cls, field_name, subtype_name)  # set default type name

            if subtype_name is None:
                return

            existing = SubtypeRegisterMixin._subtypes.get(subtype_name, None)
            if existing is not None:
                msg = 'Cant register {} as {}. Subtype {} is already registered'.format(cls, subtype_name, existing)
                from pyjackson.generics import Serializer
                if issubclass(cls, Serializer):
                    # allow reregistration if cls is generic type and it's base was registered during declaration
                    if cls._is_dynamic:
                        # do not register initialized generics
                        return
                    if issubclass(existing, Serializer) and issubclass(cls, existing):
                        # raise if cls is child of existing and does not declare type alias
                        raise ValueError(msg)
                elif existing != cls and not allow_reregistration:  # it's not serializer and different class
                    raise ValueError(msg)
            SubtypeRegisterMixin._subtypes[subtype_name] = cls

    def class_wrap(root_cls):
        wrapped = type(root_cls.__name__, (root_cls, SubtypeRegisterMixin), {})
        wrapped.__module__ = root_cls.__module__
        wrapped.__doc__ = root_cls.__doc__
        wrapped.__qualname__ = root_cls.__qualname__
        setattr(wrapped, TYPE_FIELD_NAME_FIELD_ROOT, wrapped)
        return wrapped

    return class_wrap


def real_types(*types):
    """Register multiple real types for one serializer"""

    def dec(cls):
        for t in types:
            _register_serializer(cls, t)
        return cls

    return dec


def rename_fields(**field_mapping):
    """
    Change name of fields in payload. This behavior is inheritable and overridable for child classes

    :param field_mapping: str-str mapping of field name (from constructor) to field name in payload
    """

    def decorator(cls):
        if hasattr(cls, FIELD_MAPPING_NAME_FIELD):
            mapping, new_mapping = copy(getattr(cls, FIELD_MAPPING_NAME_FIELD)), field_mapping
            mapping.update(new_mapping)
        else:
            mapping = field_mapping
        setattr(cls, FIELD_MAPPING_NAME_FIELD, mapping)
        return cls

    return decorator


def camel_case(cls):
    """
    Change snake_case field names to camelCase names
    """
    fields = get_class_field_names(cls)
    rename = {}
    for f in fields:
        tokens = f.split('_')
        rename[f] = tokens[0] + ''.join(t.capitalize() for t in tokens[1:])
    return rename_fields(**rename)(cls)
