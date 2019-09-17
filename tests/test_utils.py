from typing import Coroutine, Dict, List, Set, Tuple, Union

from pyjackson.utils import (cached_property, get_collection_internal_type, get_mapping_types, is_collection,
                             is_generic, is_mapping, is_union, make_string, union_args)

# __all__ = ['type_field', 'resolve_sequence_type', 'is_aslist',
#            'type_field_position_is', 'union_args', 'get_collection_internal_type', 'get_mapping_types',
#            'get_class_fields', 'as_list', 'get_function_fields', 'argspec_to_fields', 'get_collection_type',
#            'get_function_signature', 'get_subtype_alias', 'get_type_field_name', 'has_hierarchy', 'resolve_subtype',
#            'is_generic', 'issubclass_safe', 'is_hierarchy_root', 'turn_args_to_kwargs', 'flat_dict_repr',
#            'has_subtype_alias', 'is_serializable', 'is_descriptor', 'cached_property']


def test_make_string():
    @make_string
    class AClass:
        def __init__(self, field):
            self.field = field

    assert str(AClass('value')) == 'AClass(field=value)'


def test_is_mapping():
    assert is_mapping(Dict)
    assert is_mapping(Dict[str, str])
    assert not is_mapping(List)
    assert not is_mapping(List[str])


def test_is_generic():
    assert is_generic(List)
    assert is_generic(Dict)
    assert is_generic(List[str])
    assert not is_generic(list)


def test_is_union():
    assert is_union(Union)
    assert is_union(Union[str, List[str]])
    assert is_union(Union[str, None])
    assert not is_union(List)
    assert not is_union(List[str])


def test_is_collection():
    assert is_collection(List)
    assert is_collection(List[str])
    assert is_collection(Tuple)
    assert is_collection(Tuple[str])
    assert is_collection(Set)
    assert is_collection(Set[str])
    assert not is_collection(Coroutine)


def test_get_mapping_types():
    assert get_mapping_types(Dict[str, int]) == (str, int)
    assert get_mapping_types(Dict[str, List[str]]) == (str, List[str])


def test_get_collection_internal_type():
    assert get_collection_internal_type(List[str]) == str
    assert get_collection_internal_type(List[List[str]]) == List[str]


def test_union_args():
    assert union_args(Union[str, int]) == (str, int)
    assert union_args(Union[List[str], List[int]]) == (List[str], List[int])


def test_cached_property_laziness():
    executed = [0]

    class WithCachedProperty:
        @cached_property
        def prop(self):
            executed[0] = executed[0] + 1
            return 'lol'

    assert executed[0] == 0

    wc1 = WithCachedProperty()

    assert executed[0] == 0

    id(wc1.prop)
    assert executed[0] == 1

    id(wc1.prop)
    assert executed[0] == 1


def test_cached_property_instance_uniqness():
    executed = [0]

    class WithCachedProperty:
        @cached_property
        def prop(self):
            executed[0] = executed[0] + 1
            return 'lol'

    id(WithCachedProperty().prop)
    assert executed[0] == 1

    id(WithCachedProperty().prop)
    assert executed[0] == 2
