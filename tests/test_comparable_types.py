from typing import List

from pyjackson.core import Comparable
from pyjackson.generics import Serializer


class AClass:
    pass


class CompTypeBase(Serializer, Comparable):
    pass


class CompTypeChild(CompTypeBase):
    real_type = AClass

    def __init__(self, argument: int):
        self.argument = argument


class CompTypeChildUnhashable(CompTypeBase):
    real_type = AClass

    def __init__(self, value: List[int]):
        self.value = value


def test_types_equals():
    t1 = CompTypeChild(1)
    t2 = CompTypeChild(1)
    assert t1 == t2


def test_types_not_equals():
    t1 = CompTypeChild(1)
    t2 = CompTypeChild(2)
    assert t1 != t2


def test_types_unhashable_equals():
    t1 = CompTypeChildUnhashable([1])
    t2 = CompTypeChildUnhashable([1])
    assert t1 == t2


def test_types_unhashable_not_equals():
    t1 = CompTypeChildUnhashable([1])
    t2 = CompTypeChildUnhashable([2])
    assert t1 != t2


def test_kek():
    assert List[int] == List[int]
