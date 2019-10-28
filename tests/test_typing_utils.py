from typing import Coroutine, Dict, List, Set, Tuple, Union

from pyjackson._typing_utils import (get_collection_type, is_collection, is_generic, is_mapping, is_tuple, is_union,
                                     resolve_forward_ref, resolve_inner_forward_refs)


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
    assert is_collection(Set)
    assert is_collection(Set[str])
    assert not is_collection(Coroutine)
    assert not is_collection(Dict)
    assert not is_collection(Dict[str, int])


def test_resolve_inner_forward_refs__list():
    def list_arg(a: List['A']): pass

    ann = list_arg.__annotations__['a']
    list_col = resolve_inner_forward_refs(ann, list_arg)
    assert list_col == List[A]


def test_resolve_inner_forward_refs__set():
    def set_arg(a: Set['A']): pass

    ann = set_arg.__annotations__['a']
    set_col = resolve_inner_forward_refs(ann, set_arg)
    assert set_col == Set[A]


def test_resolve_inner_forward_refs__tuple():
    def tuple_arg(a: Tuple['A', 'B', int]): pass

    ann = tuple_arg.__annotations__['a']
    tuple_col = resolve_inner_forward_refs(ann, tuple_arg)
    assert tuple_col == Tuple[A, B, int]


class A:
    pass


class B:
    pass


def test_get_collection_type():
    assert get_collection_type(List[str]) == list
    assert get_collection_type(Set[str]) == set
    assert get_collection_type(Tuple[str]) == tuple


def test_resolve_forward_ref():
    forward_ref = Tuple['A'].__args__[0]
    not_forward_ref = Tuple[A].__args__[0]
    assert resolve_forward_ref(forward_ref, test_resolve_forward_ref.__globals__) == A
    assert resolve_forward_ref(not_forward_ref, test_resolve_forward_ref.__globals__) == A


def test_is_tuple():
    class A:
        pass

    assert is_tuple(Tuple)
    assert is_tuple(Tuple[int])
    assert is_tuple(Tuple[int, ...])
    assert not is_tuple(List)
    assert not is_tuple(List[str])
    assert not is_tuple(A)
