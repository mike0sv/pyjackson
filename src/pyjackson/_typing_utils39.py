import collections.abc
import typing


def _is_alias(as_class: typing.Type):
    return isinstance(as_class, (typing._SpecialGenericAlias, typing._GenericAlias))


def is_generic39(as_class: typing.Type):
    return _is_alias(as_class) and as_class.__origin__ not in (
        typing.Union, typing.ClassVar, collections.abc.Callable
    )


_collection_types = [
    collections.abc.Collection,
]


def is_collection39(as_class):
    return is_generic39(as_class) and any(issubclass(as_class.__origin__, t) for t in _collection_types) and \
           not issubclass(as_class.__origin__, dict)


def resolve_forward_ref39(type_hint, globals__):
    if isinstance(type_hint, typing.ForwardRef):
        type_hint = type_hint._evaluate(globals__, None, set())
    return type_hint


def resolve_inner_forward_refs39(type_hint, f):
    if is_generic39(type_hint):
        glob = getattr(f, '__globals__', {})
        args = [resolve_forward_ref39(a, glob) for a in type_hint.__args__]
        type_hint = type_hint.copy_with(tuple(args))
    return type_hint


def is_mapping39(as_class):
    return is_generic39(as_class) and issubclass(as_class.__origin__, collections.abc.Mapping)


def is_tuple39(as_class):
    return _is_alias(as_class) and as_class.__origin__ is tuple
