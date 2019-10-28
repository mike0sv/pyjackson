import collections.abc
import typing


def is_generic37(as_class: typing.Type):
    return isinstance(as_class, typing._GenericAlias) and as_class.__origin__ not in (
        typing.Union, typing.ClassVar, collections.abc.Callable
    )


_collection_types = [
    collections.abc.Collection,
]


def is_collection37(as_class):
    return is_generic37(as_class) and any(issubclass(as_class.__origin__, t) for t in _collection_types) and \
           not issubclass(as_class.__origin__, dict)


def resolve_forward_ref37(type_hint, globals__):
    if isinstance(type_hint, typing.ForwardRef):
        type_hint = type_hint._evaluate(globals__, None)
    return type_hint


def resolve_inner_forward_refs37(type_hint, f):
    if is_generic37(type_hint):
        glob = getattr(f, '__globals__', {})
        args = [resolve_forward_ref37(a, glob) for a in type_hint.__args__]
        type_hint = type_hint.copy_with(tuple(args))
    return type_hint


def is_union37(cls):
    return cls == typing.Union or (hasattr(cls, '__origin__') and cls.__origin__ == typing.Union)


def is_mapping37(as_class):
    return is_generic37(as_class) and issubclass(as_class.__origin__, collections.abc.Mapping)


def get_collection_type37(as_class: type):
    return as_class.__origin__


def is_tuple37(as_class):
    return isinstance(as_class, typing._GenericAlias) and as_class.__origin__ is tuple
