import typing


def is_generic35(as_class: typing.Type):
    return isinstance(as_class, typing.GenericMeta)


def is_collection35(as_class):
    return issubclass(as_class, (typing.List, typing.Set, typing.Tuple))


def resolve_sequence_type35(type_hint, f):
    if is_generic35(type_hint) and is_collection35(type_hint):
        seq_type = type_hint.__args__[0]
        if isinstance(seq_type, typing._ForwardRef):
            globals__ = f.__globals__
            seq_type = seq_type._eval_type(globals__, {})
            type_hint = typing.Sequence[seq_type]
    return type_hint


def is_union35(cls):
    try:
        return isinstance(cls, typing.UnionMeta)
    except AttributeError:
        return isinstance(cls, typing._UnionMeta)


def is_mapping35(as_class):
    return issubclass(as_class, typing.Mapping)


def get_collection_type35(as_class: type):
    if issubclass(as_class, typing.List):
        return list
    elif issubclass(as_class, typing.Set):
        return set
    elif issubclass(as_class, typing.Tuple):
        return tuple
    raise ValueError('Unknown sequence type {}'.format(as_class))
