import typing


def is_generic35(as_class: typing.Type):
    return isinstance(as_class, typing.GenericMeta)


def is_collection35(as_class):
    return issubclass(as_class, (typing.List, typing.Set))


def resolve_forward_ref35(type_hint, globals__):
    if isinstance(type_hint, typing._ForwardRef):
        type_hint = type_hint._eval_type(globals__, None)
    return type_hint


def resolve_inner_forward_refs35(type_hint, f):
    if is_generic35(type_hint):
        glob = getattr(f, '__globals__', {})
        args = [resolve_forward_ref35(a, glob) for a in type_hint.__args__]
        type_hint = type_hint.__origin__[tuple(args)]
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


def is_tuple35(as_class):
    return issubclass(as_class, typing.Tuple)
