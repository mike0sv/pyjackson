from typing import Any, Hashable, List, Set, Tuple, Type

from pyjackson.core import BUILTIN_TYPES, FIELD_MAPPING_NAME_FIELD, Position
from pyjackson.errors import SerializationError, UnserializableError
from pyjackson.generics import SERIALIZER_MAPPING, Serializer, SerializerType, StaticSerializer
from pyjackson.utils import (get_class_fields, get_type_field_name, has_serializer, is_aslist, is_serializable,
                             is_union, issubclass_safe, type_field_position_is, union_args)


def _serialize_to_dict(cls, obj):
    result = {}
    fields = get_class_fields(cls)
    for f in fields:
        name = f.name
        field = getattr(obj, name)
        if field is not None:
            if hasattr(cls, FIELD_MAPPING_NAME_FIELD):
                name = getattr(cls, FIELD_MAPPING_NAME_FIELD).get(name, name)
            result[name] = serialize(field, f.type)

    if type_field_position_is(cls, Position.INSIDE):
        type_field_name = get_type_field_name(cls)
        if type_field_name in result:
            raise SerializationError(
                'Type field name {} conflicts with field name in {}'.format(type_field_name, cls))
        result[type_field_name] = getattr(cls, type_field_name)
    return result


def _serialize_to_list(cls, obj):
    result = []
    fields = get_class_fields(cls)
    for f in fields:
        name = f.name
        field = getattr(obj, name)
        if field is not None:
            result.append(serialize(field))

    if type_field_position_is(cls, Position.INSIDE):
        type_field_name = get_type_field_name(cls)
        result = [getattr(cls, type_field_name)] + result
    return result


def _serialize_to(as_class, obj):
    if is_aslist(as_class):
        return _serialize_to_list(as_class, obj)
    else:
        return _serialize_to_dict(as_class, obj)


def _serialize_union(obj, class_union):
    for as_class in union_args(class_union):
        try:
            return serialize(obj, as_class)
        except SerializationError:
            pass
    else:
        raise SerializationError('None of the possible types matched for obj {} and type {}'.format(obj, class_union))


def _serialize_with_serializer(obj, serializer: Serializer):
    if issubclass_safe(serializer, StaticSerializer):
        return serializer.serialize(obj)

    if not serializer._is_dynamic:
        raise SerializationError('Cannot use uninitialized serializer. '
                                 'Initialize it or replace with StaticSerializer')
    return serializer.serialize(obj)


def _serialize_as_type(obj, as_class: Type):
    if any(isinstance(obj, t) for t in [List, Set, Tuple]):
        return [serialize(o) for o in obj]
    elif isinstance(obj, dict):
        return {key: serialize(value) for key, value in obj.items()}
    elif isinstance(as_class, Hashable) and as_class in BUILTIN_TYPES:
        return obj
    else:
        return _serialize_to(as_class, obj)


def serialize(obj, as_class: SerializerType = None):
    """
    Convert object into JSON-compatible dict (or other  structure)

    :param obj: object to serialize
    :param as_class: type to serialize as or serializer

    :return: JSON-compatible object
    """
    if as_class is Any:
        return obj
    if not is_serializable(obj):
        raise UnserializableError(obj)

    is_serializer_hierarchy = (issubclass_safe(as_class, Serializer)
                               and issubclass_safe(obj, as_class)
                               and not as_class._is_dynamic and obj._is_dynamic)
    if issubclass_safe(obj, Serializer) and (as_class is None or is_serializer_hierarchy):
        # serialize type itself
        return _serialize_to(obj, obj)

    if is_union(as_class):
        return _serialize_union(obj, as_class)

    obj_type = type(obj)
    # as_class not specified or obj_type is subclass of as_class
    if as_class is None or issubclass_safe(obj_type, as_class) and not issubclass_safe(as_class, Serializer):
        as_class = obj_type

    # as_class has registered serializer
    if has_serializer(as_class):
        as_class = SERIALIZER_MAPPING[as_class]

    # as_class is serializer
    if issubclass_safe(as_class, Serializer):
        return _serialize_with_serializer(obj, as_class)

    # as_class is just regular type
    return _serialize_as_type(obj, as_class)
