import collections.abc
import typing


def is_generic37(as_class: typing.Type):
    return isinstance(as_class, typing._GenericAlias) and as_class.__origin__ not in (
        typing.Union, typing.ClassVar, collections.abc.Callable
    )


_collection_types = [
    collections.abc.Collection,
    tuple
]


def is_collection37(as_class):
    return is_generic37(as_class) and any(issubclass(as_class.__origin__, t) for t in _collection_types)


def resolve_sequence_type37(type_hint, f):
    if is_collection37(type_hint):
        seq_type = type_hint.__args__[0]
        if isinstance(seq_type, typing.ForwardRef):
            globals__ = f.__globals__
            seq_type = seq_type._evaluate(globals__, globals__)
            type_hint = typing.Sequence[seq_type]

    return type_hint


def is_union37(cls):
    return cls == typing.Union or (hasattr(cls, '__origin__') and cls.__origin__ == typing.Union)


def is_mapping37(as_class):
    return is_generic37(as_class) and issubclass(as_class.__origin__, collections.abc.Mapping)


def get_collection_type37(as_class: type):
    return as_class.__origin__
