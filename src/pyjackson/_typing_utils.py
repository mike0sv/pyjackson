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
                                  is_tuple35 as is_tuple)

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
                                  is_tuple37 as is_tuple)

else:
    warnings.warn('Pyjackson was not tested for python version > 3.8')

__all__ = [
    'resolve_inner_forward_refs',
    'is_collection',
    'is_generic',
    'is_mapping', 'is_union',
    'get_collection_type',
    'resolve_forward_ref',
    'is_tuple'
]
