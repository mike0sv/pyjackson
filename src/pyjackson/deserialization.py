from typing import Hashable, Type

from pyjackson.core import BUILTIN_TYPES, Field, Position
from pyjackson.errors import DeserializationError
from pyjackson.generics import SERIALIZER_MAPPING, Serializer, SerializerType, StaticSerializer
from pyjackson.utils import (get_class_fields, get_collection_internal_type, get_collection_type, get_mapping_types,
                             get_tuple_internal_types, has_subtype_alias, is_aslist, is_collection, is_generic,
                             is_hierarchy_root, is_mapping, is_tuple, is_union, resolve_subtype, type_field_position_is,
                             union_args)


def _get_field_type(field: Field, obj):
    field_type = field.type
    # type is in parent, ex: {'shape_type':'box', 'shape':{'coords':...}}
    if type_field_position_is(field_type, Position.OUTSIDE):
        field_type = resolve_subtype(field_type, obj)
    return field_type


def _construct_from_list(obj, as_class):
    args = []
    if type_field_position_is(as_class, Position.INSIDE):
        obj = obj[1:]
    for i, f in enumerate(get_class_fields(as_class)):
        field_type = _get_field_type(f, obj)

        if i >= len(obj):
            if f.has_default:
                continue
            else:
                raise ValueError("Too few arguments for type  {} ".format(as_class))
        else:
            args.append(deserialize(obj[i], field_type))
    return as_class(*args)


def _construct_from_dict(obj, as_class):
    kwargs = {}
    for f in get_class_fields(as_class):
        field_name = f.name
        field_type = _get_field_type(f, obj)

        if field_name not in obj:
            if f.has_default:
                continue
            else:
                raise ValueError("Type {} has required argument {}".format(as_class, field_name))
        else:
            kwargs[field_name] = deserialize(obj[field_name], field_type)
    return as_class(**kwargs)


def _construct_from(obj, as_class):
    if is_aslist(as_class):
        return _construct_from_list(obj, as_class)
    else:
        return _construct_from_dict(obj, as_class)


def _construct_object(obj, as_class: Type):
    if isinstance(as_class, Hashable) and as_class in SERIALIZER_MAPPING:
        as_class = SERIALIZER_MAPPING[as_class]

    if issubclass(as_class, StaticSerializer):
        return as_class.deserialize(obj)
    elif issubclass(as_class, Serializer):
        if as_class._is_dynamic:
            return as_class.deserialize(obj)
        else:
            # construct type itself
            return _construct_from(obj, as_class)

    return _construct_from(obj, as_class)


def deserialize(obj, as_class: SerializerType):
    """Convert python dict into given class

    :param obj: dict (or list or any primitive) to deserialize
    :param as_class: type or serializer

    :return: deserialized instance of as_class (or real_type of serializer)

    :raise: DeserializationError
    """
    if is_generic(as_class):
        if is_mapping(as_class):
            key_type, value_type = get_mapping_types(as_class)
            if key_type != str:
                raise DeserializationError(
                    'mapping key type must be str, not {}. error deserializing {}'.format(key_type, obj))
            return {k: deserialize(v, value_type) for k, v in obj.items()}
        elif is_tuple(as_class):
            var_length, types = get_tuple_internal_types(as_class)
            if var_length:
                return tuple(deserialize(o, types) for o in obj)
            else:
                return tuple(deserialize(o, t) for o, t in zip(obj, types))
        elif is_collection(as_class):
            seq_int_type = get_collection_internal_type(as_class)
            seq_type = get_collection_type(as_class)
            return seq_type([deserialize(o, seq_int_type) for o in obj])
    elif isinstance(as_class, Hashable) and as_class in BUILTIN_TYPES:
        return obj
    else:
        if not is_union(as_class):
            if type_field_position_is(as_class, Position.INSIDE) and (is_hierarchy_root(as_class) or
                                                                      has_subtype_alias(as_class, obj)):
                as_class = resolve_subtype(as_class, obj)
            return _construct_object(obj, as_class)
        else:
            for possible_type in union_args(as_class):
                try:
                    return deserialize(obj, possible_type)
                except TypeError:
                    pass
            else:
                raise DeserializationError("Cannot construct type {} from argument list {}".format(as_class, obj))
