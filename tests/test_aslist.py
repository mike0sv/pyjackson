from pyjackson.decorators import as_list, make_string, type_field
from pyjackson.utils import Comparable
from tests.conftest import serde_and_compare


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


def test_simple():
    obj = SimpleAL(1, 'a')
    serde_and_compare(obj, true_payload=[1, 'a'])


def test_hierarchy_ser():
    obj = ChildAL('b')
    serde_and_compare(obj, true_payload=['child_al', 'b'])
