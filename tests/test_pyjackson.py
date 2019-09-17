from typing import Dict, List, Set, Tuple, Union

import pyjackson as pyjackson
from pyjackson.comparable import Comparable
from pyjackson.utils import make_string, type_field
from tests.conftest import serde_and_compare


@make_string
class Foo(Comparable):
    def __init__(self, bar: str):
        self.bar = bar


@make_string
class InDict(Comparable):
    def __init__(self, foos: Dict[str, Foo]):
        self.foos = foos


@make_string
class HintAndDefault(Comparable):
    def __init__(self, foo: Foo = None):
        self.foo = foo


@make_string
class HintAndDefaultDict(Comparable):
    def __init__(self, foos: Dict[str, Foo] = None):
        self.foos = foos


@make_string
class OptionalNone(Comparable):
    def __init__(self, field: List[Union[int, None]]):
        self.field = field


@make_string
class TupleTest(Comparable):
    def __init__(self, field: Tuple[int, ...]):
        self.field = field


@make_string
class SetTest(Comparable):
    def __init__(self, field: Set[int]):
        self.field = field


@type_field('type')
class Parent(Comparable):
    type = None

    def __new__(cls, *args, **kwargs):
        assert cls != Parent, 'parent is not supposed to be initialized'
        return super().__new__(cls)


@make_string
class Child(Parent):
    type = 'first'


@make_string
class SecondChild(Child):
    type = 'second'

    def __init__(self, field: str):
        self.field = field


@make_string
class WithHierarchyAsField(Comparable):
    def __init__(self, field: Parent):
        self.field = field


def test_comparable():
    class C(Comparable):
        def __init__(self, param: str):
            self.param = param

    c1 = C('1')
    c2 = C('2')
    c1_2 = C('1')

    assert c1 == c1_2
    assert c1 != c2


def test_type_hint_with_default_exists():
    serde_and_compare(HintAndDefault(Foo('kek')), true_payload={'foo': {'bar': 'kek'}})


def test_type_hint_with_default_not_exists():
    serde_and_compare(HintAndDefault())


def test_type_hint_with_default_dict_exists():
    serde_and_compare(HintAndDefaultDict({'test': Foo('kek')}))


def test_type_hint_with_default_dict_not_exists():
    serde_and_compare(HintAndDefaultDict())


def test_hierarchy():
    obj = Child()
    serde_and_compare(obj, Parent)


def test_type_field_addition():
    c = SecondChild('test')
    data = pyjackson.serialize(c)

    assert 'type' in data


def test_hierarchy_skip():
    obj = SecondChild('test')
    serde_and_compare(obj, Child, true_payload={'type': 'second', 'field': 'test'})


def test_hierarchy_field():
    obj = WithHierarchyAsField(SecondChild('a'))
    serde_and_compare(obj, true_payload={'field': {'type': 'second', 'field': 'a'}})


def test_optional_none():
    obj1 = OptionalNone([1])
    obj2 = OptionalNone([None])

    serde_and_compare(obj1, true_payload={'field': [1]})
    serde_and_compare(obj2, true_payload={'field': [None]})


def test_seq():
    obj1 = TupleTest((1, 2))
    serde_and_compare(obj1, true_payload={'field': [1, 2]})

    obj1 = SetTest({1, 2})
    serde_and_compare(obj1, true_payload={'field': [1, 2]})


def test_explicit_child():
    obj = SecondChild('aaa')

    serde_and_compare(obj, SecondChild, {'field': 'aaa'}, check_payload=False)