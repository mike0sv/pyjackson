import sys

_major, _minor, *_ = sys.version_info

if _major != 3 or _minor < 5:
    raise Exception('Pyjackson works only with python version >= 3.5')

if _minor < 7:
    from ._typing_utils35 import (resolve_sequence_type35 as resolve_sequence_type,
                                  is_generic35 as is_generic,
                                  is_mapping35 as is_mapping,
                                  get_collection_type35 as get_collection_type)

    if _minor == 5:
        from ._typing_utils35 import is_union35 as is_union, is_collection35 as is_collection
    else:
        from ._typing_utils36 import is_union36 as is_union, is_collection36 as is_collection

elif _minor == 7:
    from ._typing_utils37 import (resolve_sequence_type37 as resolve_sequence_type,
                                  is_collection37 as is_collection,
                                  is_generic37 as is_generic,
                                  is_mapping37 as is_mapping,
                                  is_union37 as is_union,
                                  get_collection_type37 as get_collection_type)
else:
    raise Exception('Pyjackson works only with python version <= 3.7 yet(')

__all__ = [
    'resolve_sequence_type',
    'is_collection',
    'is_generic',
    'is_mapping', 'is_union',
    'get_collection_type',
]
