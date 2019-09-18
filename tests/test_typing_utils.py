from typing import Coroutine, Dict, List, Set, Tuple, Union

from pyjackson._typing_utils import (get_collection_type, is_collection, is_generic, is_mapping, is_union,
                                     resolve_sequence_type)
from pyjackson.utils import get_collection_internal_type


def test_is_generic():
    assert is_generic(List)
    assert is_generic(Dict)
    assert is_generic(List[str])
    assert not is_generic(list)


def test_is_mapping():
    assert is_mapping(Dict)
    assert is_mapping(Dict[str, str])
    assert not is_mapping(List)
    assert not is_mapping(List[str])


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


def test_resolve_sequence_type():
    def list_arg(a: List['A']): pass

    def set_arg(a: Set['A']): pass

    def tuple_arg(a: Tuple['A']): pass

    def tp(f):
        return f.__annotations__['a']

    assert get_collection_internal_type(resolve_sequence_type(tp(list_arg), list_arg)) == A
    assert get_collection_internal_type(resolve_sequence_type(tp(set_arg), set_arg)) == A
    assert get_collection_internal_type(resolve_sequence_type(tp(tuple_arg), tuple_arg)) == A


class A:
    pass


def test_get_collection_type():
    assert get_collection_type(List[str]) == list
    assert get_collection_type(Set[str]) == set
    assert get_collection_type(Tuple[str]) == tuple
