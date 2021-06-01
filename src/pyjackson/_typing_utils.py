import sys
import warnings

_major, _minor, *_ = sys.version_info

if _major != 3 or _minor < 5:
    raise Exception('Pyjackson works only with python version >= 3.5')

if _minor < 7:
    from ._typing_utils35 import (is_generic35 as is_generic,
                                  is_mapping35 as is_mapping,
                                  get_collection_type35 as get_collection_type,
                                  resolve_forward_ref35 as resolve_forward_ref,
                                  resolve_inner_forward_refs35 as resolve_inner_forward_refs,
                                  is_tuple35 as is_tuple,
                                  get_generic_origin35 as get_generic_origin)

    if _minor == 5:
        from ._typing_utils35 import is_union35 as is_union, is_collection35 as is_collection
    else:
        from ._typing_utils36 import is_union36 as is_union, is_collection36 as is_collection

elif _minor <= 8:
    from ._typing_utils37 import (is_collection37 as is_collection,
                                  is_generic37 as is_generic,
                                  is_mapping37 as is_mapping,
                                  is_union37 as is_union,
                                  get_collection_type37 as get_collection_type,
                                  resolve_forward_ref37 as resolve_forward_ref,
                                  resolve_inner_forward_refs37 as resolve_inner_forward_refs,
                                  is_tuple37 as is_tuple,
                                  get_generic_origin37 as get_generic_origin)

else:
    from ._typing_utils37 import (is_union37 as is_union,
                                  get_collection_type37 as get_collection_type,
                                  get_generic_origin37 as get_generic_origin)
    from ._typing_utils39 import (is_collection39 as is_collection,
                                  is_generic39 as is_generic,
                                  is_mapping39 as is_mapping,
                                  resolve_forward_ref39 as resolve_forward_ref,
                                  resolve_inner_forward_refs39 as resolve_inner_forward_refs,
                                  is_tuple39 as is_tuple,)

    if _minor > 9:
        warnings.warn('Pyjackson was not tested for python version > 3.9')


def is_generic_or_union(cls):
    return is_generic(cls) or is_union(cls)


def get_type_name_repr(cls):
    if is_generic(cls):
        typename = getattr(cls, '_name', str(cls.__origin__))
        if typename.startswith('typing.'):
            typename = typename[len('typing.'):]
        return f'{typename}[{", ".join(get_type_name_repr(c) for c in cls.__args__)}]'
    elif is_union(cls):
        typename = str(cls.__origin__)
        if typename.startswith('typing.'):
            typename = typename[len('typing.'):]
        return f'{typename}[{", ".join(get_type_name_repr(c) for c in cls.__args__)}]'
    elif isinstance(cls, str):
        return cls
    else:
        return getattr(cls, '__name__', str(cls))


__all__ = [
    'resolve_inner_forward_refs',
    'is_collection',
    'is_generic',
    'is_mapping', 'is_union',
    'get_collection_type',
    'resolve_forward_ref',
    'is_tuple',
    'get_generic_origin',
    'is_generic_or_union',
    'get_type_name_repr'
]
