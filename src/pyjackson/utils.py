import inspect
import sys
import typing
from copy import copy

from pyjackson.core import (CLASS_SPECS_CACHE, TYPE_AS_LIST, TYPE_FIELD_NAME_FIELD_NAME, TYPE_FIELD_NAME_FIELD_POSITION,
                            TYPE_FIELD_NAME_FIELD_ROOT, Position, PyjacksonError, Unserializable)

_major, _minor, *_ = sys.version_info

if _major != 3 or _minor < 5:
    raise Exception('Pyjackson works only with python version >= 3.5')

if _minor < 7:
    from ._utils35 import (resolve_sequence_type35 as resolve_sequence_type,
                           is_generic35 as is_generic,
                           is_mapping35 as is_mapping,
                           get_collection_type35 as get_collection_type)

    if _minor == 5:
        from ._utils35 import is_union35 as is_union, is_collection35 as is_collection
    else:
        from ._utils36 import is_union36 as is_union, is_collection36 as is_collection

elif _minor == 7:
    from ._utils37 import (resolve_sequence_type37 as resolve_sequence_type,
                           is_collection37 as is_collection,
                           is_generic37 as is_generic,
                           is_mapping37 as is_mapping,
                           is_union37 as is_union,
                           get_collection_type37 as get_collection_type)
else:
    raise Exception('Pyjackson works only with python version <= 3.7 yet(')

__all__ = ['make_string', 'type_field', 'resolve_sequence_type', 'is_collection', 'is_union', 'is_mapping', 'is_aslist',
           'type_field_position_is', 'union_args', 'get_collection_internal_type', 'get_mapping_types',
           'get_class_fields', 'as_list', 'get_function_fields', 'argspec_to_fields', 'get_collection_type',
           'get_function_signature', 'get_subtype_alias', 'get_type_field_name', 'has_hierarchy', 'resolve_subtype',
           'is_generic', 'issubclass_safe', 'is_hierarchy_root', 'turn_args_to_kwargs', 'flat_dict_repr',
           'has_subtype_alias', 'is_serializable', 'is_descriptor', 'cached_property', 'Field', 'Signature', 'ArgList']


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
    """Decorator to create a __str__ method for class based on __init__ arguments
    Usage: directly @make_string on class defenition or @make_string(include_name=True) to include class name
    """
    if len(fields) == 1 and not isinstance(fields[0], str):
        cls = fields[0]
        fields = []
    else:
        cls = None

    def make_str(cls):
        def __str__(self):
            flds = fields or [f.name for f in get_function_fields(cls.__init__, False)]
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


def flat_dict_repr(d: dict, func_order=None, sep=',', braces=False):
    if braces:
        return '{' + flat_dict_repr(d, func_order, sep, False) + '}'

    if func_order is None:
        order = d.keys()
    else:
        order = [f.name for f in get_function_fields(func_order, types_required=False)]
    return sep.join('{}={}'.format(k, d[k]) for k in order)


@make_string('name', 'type', include_name=True)
class Field:
    def __init__(self, name, type, has_default, default=None):
        self.name = name
        self.type = type
        self.has_default = has_default
        self.default = default


ArgList = typing.List[Field]
Signature = typing.NamedTuple('Signature', [('args', ArgList), ('output', Field)])


def is_aslist(cls: typing.Type):
    return hasattr(cls, TYPE_AS_LIST) and getattr(cls, TYPE_AS_LIST)


def as_list(cls: typing.Type):
    setattr(cls, TYPE_AS_LIST, True)
    return cls


def get_function_signature(f) -> Signature:
    ret = Field(None, f.__annotations__.get('return'), False)
    return Signature(get_function_fields(f), ret)


def get_function_fields(f, types_required=True) -> typing.List[Field]:
    spec = inspect.getfullargspec(f)
    arguments = spec.args
    if inspect.ismethod(f) or arguments[0] == 'self':  # TODO better method detection
        arguments = arguments[1:]
    defaults = spec.defaults
    hints = typing.get_type_hints(f)

    return argspec_to_fields(f, arguments, defaults, hints, types_required=types_required)


def argspec_to_fields(f, arguments, defaults, hints, types_required=True) -> typing.List[Field]:
    defaults_num = len(defaults) if defaults is not None else 0
    non_defaults_num = len(arguments) - defaults_num
    fields = []
    for i, arg in enumerate(arguments):
        has_default = i >= non_defaults_num
        if arg not in hints and types_required:
            raise PyjacksonError('arguments must be typehinted for function {}'.format(f))
        type_hint = resolve_sequence_type(hints.get(arg), f)
        field = Field(arg, type_hint, has_default)
        if has_default:
            field.default = defaults[i - non_defaults_num]
        fields.append(field)
    return fields


def turn_args_to_kwargs(func, args, kwargs, skip_first=False):
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

        fields = argspec_to_fields(cls.__init__, arguments, defaults, hints)
        CLASS_SPECS_CACHE[cls] = fields
    return CLASS_SPECS_CACHE[cls]


def get_class_field_names(cls: type) -> typing.List[str]:
    return [f.name for f in get_class_fields(cls)]


def type_field(field_name, position: Position = Position.INSIDE, propagate=True):
    """Class decorator for polymorphic hierarchies to define class field name, where subclass's type alias will be stored
    Use it on hierarchy root class, add class field  with defined name to any subclasses
    The same field name will be used during deserialization
    """

    class SubtypeRegisterMixin:
        _subtypes = dict()

        locals()[TYPE_FIELD_NAME_FIELD_NAME] = field_name
        locals()[TYPE_FIELD_NAME_FIELD_POSITION] = position

        def __init_subclass__(cls, **kwargs):
            super(SubtypeRegisterMixin, cls).__init_subclass__(**kwargs)
            subtype_name = getattr(cls, field_name, None)
            if subtype_name is None:
                return

            existing = SubtypeRegisterMixin._subtypes.get(subtype_name, None)
            if existing is not None and existing != cls:
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
                else:
                    raise ValueError(msg)
            SubtypeRegisterMixin._subtypes[subtype_name] = cls

    def class_wrap(root_cls):
        wrapped = type('Registering{}'.format(root_cls.__name__), (root_cls, SubtypeRegisterMixin), {})
        setattr(wrapped, TYPE_FIELD_NAME_FIELD_ROOT, wrapped)
        return wrapped

    return class_wrap


def has_hierarchy(cls):
    return hasattr(cls, TYPE_FIELD_NAME_FIELD_POSITION)


def is_hierarchy_root(cls):
    return has_hierarchy(cls) and getattr(cls, TYPE_FIELD_NAME_FIELD_ROOT) == cls


def type_field_position_is(cls, position):
    return has_hierarchy(cls) and getattr(cls, TYPE_FIELD_NAME_FIELD_POSITION) == position


def get_subtype_alias(cls, obj):
    type_field_name = get_type_field_name(cls)
    if is_aslist(cls):
        return obj[0]
    if type_field_name not in obj:
        raise PyjacksonError('Can\'t find type field named "{}" in {} for type {}'.format(type_field_name, obj, cls))
    return obj[type_field_name]


def has_subtype_alias(cls, obj):
    return is_aslist(cls) or get_type_field_name(cls) in obj


def get_type_field_name(cls):
    return getattr(cls, TYPE_FIELD_NAME_FIELD_NAME)


def resolve_subtype(cls: type, obj):
    # obj must be parent object if position == OUTSIDE
    type_alias = get_subtype_alias(cls, obj)
    return cls._subtypes[type_alias]


def get_mapping_types(as_class: typing.Type):
    key_type, value_type = as_class.__args__
    return key_type, value_type


def get_collection_internal_type(as_class: typing.Type):
    seq_type = as_class.__args__[0]
    return seq_type


def union_args(cls):
    try:
        return cls.__args__
    except Exception:
        return cls.__union_params__


def issubclass_safe(cls, classinfo):
    try:
        return issubclass(cls, classinfo)
    except TypeError:
        return False


def is_descriptor(obj):
    return any(hasattr(obj, a) for a in ['__get__', '__set__', '__delete__'])


def is_serializable(obj) -> bool:  # TODO add recursive check for builtin unser types like bytes
    return not isinstance(obj, Unserializable)


class ArgHashable:
    @cached_property
    def __hash_args__(self):
        return inspect.getfullargspec(self.__class__.__init__).args[1:]

    def __hash__(self):
        return hash((self.__class__.__name__,) + tuple(getattr(self, a) for a in self.__hash_args__))
