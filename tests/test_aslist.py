from pyjackson import deserialize, serialize
from pyjackson.comparable import Comparable
from pyjackson.utils import as_list, make_string, type_field


@as_list
class SimpleAL(Comparable):
    def __init__(self, a: int, b: str):
        self.b = b
        self.a = a


@type_field('type')
@as_list
class ParentAL(Comparable):
    type = None


@make_string('a', include_name=True)
class ChildAL(ParentAL):
    type = 'child_al'

    def __init__(self, a: str):
        self.a = a


def test_simple_ser():
    assert [1, 'a'] == serialize(SimpleAL(1, 'a'))


def test_simple_deser():
    assert SimpleAL(1, 'a') == deserialize([1, 'a'], SimpleAL)


def test_hierarchy_ser():
    assert ['child_al', 'b'] == serialize(ChildAL('b'))


def test_hierarchy_deser():
    assert ChildAL('b') == deserialize(['child_al', 'b'], ParentAL)
