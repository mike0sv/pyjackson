import inspect
import typing
from copy import copy
from importlib import import_module

from pyjackson import generics
from pyjackson.core import (BUILTIN_TYPES, CLASS_SPECS_CACHE, TYPE_AS_LIST, TYPE_FIELD_NAME_FIELD_NAME,
                            TYPE_FIELD_NAME_FIELD_POSITION, TYPE_FIELD_NAME_FIELD_ROOT, Comparable, Field, Position,
                            Signature, Unserializable)
from pyjackson.errors import DeserializationError, PyjacksonError

from ._typing_utils import (get_collection_type, is_collection, is_generic, is_mapping, is_tuple, is_union,
                            resolve_inner_forward_refs)

__all__ = ['resolve_inner_forward_refs', 'is_generic', 'is_mapping', 'is_union', 'is_collection', 'get_collection_type',
           'flat_dict_repr', 'is_aslist', 'get_function_fields', 'get_type_field_name',
           'get_subtype_alias', 'get_function_signature', 'get_class_fields', 'get_mapping_types',
           'get_collection_internal_type', 'get_class_field_names', '_argspec_to_fields', 'union_args',
           'turn_args_to_kwargs', 'has_subtype_alias', 'has_hierarchy', 'issubclass_safe', 'is_descriptor',
           'has_serializer', 'is_init_type_hinted_and_has_correct_attrs', 'is_serializable', 'is_hierarchy_root',
           'type_field_position_is', 'resolve_subtype', 'Comparable', 'get_tuple_internal_types', 'is_tuple']


def flat_dict_repr(d: dict, func_order=None, sep=',', braces=False):
    """
    Turn dict into string of key=value pairs, separated by sep
    :param d: the dict
    :param func_order: if passed, order of pairs will conform to order of arguments.
    key set must be the same as func arg list
    :param sep: separator
    :param braces: whether to surround with braces
    :return: string representation
    """
    if braces:
        return '{' + flat_dict_repr(d, func_order, sep, False) + '}'

    if func_order is None:
        order = d.keys()
    else:
        order = [f.name for f in get_function_fields(func_order, types_required=False)]
    return sep.join('{}={}'.format(k, d[k]) for k in order)


def is_aslist(cls: typing.Type):
    """
    Checks if cls was marked to be serialized as list

    :param cls: type to check
    :return: boolean
    """
    return hasattr(cls, TYPE_AS_LIST) and getattr(cls, TYPE_AS_LIST)


def get_function_signature(f) -> Signature:
    """
    Get function arguments as list of :class:`~pyjackson.core.Field` and annotated return type
    :param f: function
    :return: Signature named tuple
    """
    ret = Field(None, f.__annotations__.get('return'), False)
    return Signature(get_function_fields(f), ret)


def get_function_fields(f, types_required=True) -> typing.List[Field]:
    """
    Get function arguments as list of :class:`~pyjackson.core.Field`

    :param f: function
    :param types_required: raise exception if args not type hinted
    :return: list of :class:`~pyjackson.core.Field`
    """
    spec = inspect.getfullargspec(f)
    arguments = spec.args
    if inspect.ismethod(f) or arguments[0] == 'self':  # TODO better method detection
        arguments = arguments[1:]
    defaults = spec.defaults
    hints = typing.get_type_hints(f)

    return _argspec_to_fields(f, arguments, defaults, hints, types_required=types_required)


def _argspec_to_fields(f, arguments, defaults, hints, types_required=True) -> typing.List[Field]:
    defaults_num = len(defaults) if defaults is not None else 0
    non_defaults_num = len(arguments) - defaults_num
    fields = []
    for i, arg in enumerate(arguments):
        has_default = i >= non_defaults_num
        if arg not in hints and types_required:
            raise PyjacksonError('arguments must be typehinted for function {}'.format(f))
        type_hint = resolve_inner_forward_refs(hints.get(arg), f)
        field = Field(arg, type_hint, has_default)
        if has_default:
            field.default = defaults[i - non_defaults_num]
        fields.append(field)
    return fields


def turn_args_to_kwargs(func, args, kwargs, skip_first=False):
    """
    Turn *args, **kwargs into just **kwargs for specified function

    :param func: function
    :param args: *args
    :param kwargs: **kwargs
    :param skip_first: skip first arg (used for methods)
    :return: **kwargs dict
    """
    kwargs = copy(kwargs)
    fields = get_function_fields(func, types_required=False)
    if skip_first:
        fields = fields[1:]
    for field, arg in zip(fields, args):
        kwargs[field.name] = arg
    return kwargs


def get_class_fields(cls: type) -> typing.List[Field]:
    """Cache and return class's __init__ parameter names and type hint"""
    if cls not in CLASS_SPECS_CACHE:

        if hasattr(cls, '_field_types') and hasattr(cls, '_fields'):
            # NamedTuple case
            hints = cls._field_types
            arguments = cls._fields
            defaults = tuple()
        else:
            spec = inspect.getfullargspec(cls.__init__)
            arguments = spec.args[1:]
            defaults = spec.defaults
            hints = typing.get_type_hints(cls.__init__)

        fields = _argspec_to_fields(cls.__init__, arguments, defaults, hints)
        CLASS_SPECS_CACHE[cls] = fields
    return CLASS_SPECS_CACHE[cls]


def get_class_field_names(cls: type) -> typing.List[str]:
    """
    Get class field names, which must be list of `__init__` arguments

    :param cls: class
    :return: list of field names
    """
    return list(inspect.getfullargspec(cls.__init__).args[1:])


def has_hierarchy(cls):
    return hasattr(cls, TYPE_FIELD_NAME_FIELD_POSITION)


def is_hierarchy_root(cls):
    return has_hierarchy(cls) and getattr(cls, TYPE_FIELD_NAME_FIELD_ROOT) == cls


def type_field_position_is(cls, position: Position):
    return has_hierarchy(cls) and getattr(cls, TYPE_FIELD_NAME_FIELD_POSITION) == position


def get_subtype_alias(cls, obj):
    type_field_name = get_type_field_name(cls)
    if is_aslist(cls):
        return obj[0]
    if type_field_name not in obj:
        raise PyjacksonError('Can\'t find type field named "{}" in {} for type {}'.format(type_field_name, obj, cls))
    return obj[type_field_name]


def has_subtype_alias(cls, obj):
    return is_aslist(cls) or (isinstance(obj, dict) and get_type_field_name(cls) in obj)


def get_type_field_name(cls):
    return getattr(cls, TYPE_FIELD_NAME_FIELD_NAME)


def resolve_subtype(cls: type, obj):
    # obj must be parent object if position == OUTSIDE
    type_alias = get_subtype_alias(cls, obj)
    if '.' in type_alias:
        try:
            split = type_alias.split('.')
            module = '.'.join(split[:-1])
            import_module(module)
        except ImportError:
            pass
    subtype = cls._subtypes.get(type_alias, None)
    if subtype is None:
        raise DeserializationError(f'Unknown subtype {type_alias} of type {cls.__name__}')
    return subtype


def get_mapping_types(as_class: typing.Type):
    key_type, value_type = as_class.__args__
    return key_type, value_type


def get_collection_internal_type(as_class: typing.Type):
    seq_type = as_class.__args__[0]
    return seq_type


def get_tuple_internal_types(as_class):
    args = as_class.__args__
    if args[-1] is ...:
        return True, args[0]
    else:
        return False, args


def union_args(cls):
    try:
        return cls.__args__
    except AttributeError:
        return cls.__union_params__


def issubclass_safe(cls, classinfo):
    try:
        return issubclass(cls, classinfo)
    except TypeError:
        return False


def is_descriptor(obj):
    return any(hasattr(obj, a) for a in ['__get__', '__set__', '__delete__'])


def has_serializer(as_class: typing.Type):
    return isinstance(as_class, typing.Hashable) and \
           as_class in generics.SERIALIZER_MAPPING and \
           not isinstance(as_class, generics.Serializer)


def is_init_type_hinted_and_has_correct_attrs(obj):
    try:
        class_fields = get_class_fields(type(obj))
    except PyjacksonError:
        return False
    return all(hasattr(obj, a.name) for a in class_fields)


def is_serializable(obj) -> bool:
    return not isinstance(obj, Unserializable) and \
           (has_serializer(type(obj)) or is_init_type_hinted_and_has_correct_attrs(obj) or type(obj) in BUILTIN_TYPES)
