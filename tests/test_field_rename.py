from pyjackson.core import Comparable
from pyjackson.decorators import camel_case, rename_fields
from tests.conftest import serde_and_compare


@rename_fields(field1='field_1')
class Parent(Comparable):
    def __init__(self, field1: str):
        self.field1 = field1


def test_rename__parent():
    obj = Parent('aaaa')

    serde_and_compare(obj, true_payload={'field_1': 'aaaa'})


class Child(Parent):
    def __init__(self, field1: str):
        super().__init__(field1)


def test_rename__child():
    obj = Child('aaaa')

    serde_and_compare(obj, true_payload={'field_1': 'aaaa'})


@rename_fields(field1='1field')
class ChildOverride(Parent):
    def __init__(self, field1: str):
        super().__init__(field1)


def test_rename__child_override():
    obj = ChildOverride('aaaa')

    serde_and_compare(obj, true_payload={'1field': 'aaaa'})


@rename_fields(field2='field_2')
class ChildExtend(Parent):
    def __init__(self, field1: str, field2: str):
        super().__init__(field1)
        self.field2 = field2


def test_rename__child_extend():
    obj = ChildExtend('aaaa', 'bbbb')

    serde_and_compare(obj, true_payload={'field_1': 'aaaa', 'field_2': 'bbbb'})


@camel_case
class CamelCase(Comparable):
    def __init__(self, field_one: str, field_two: str):
        self.field_one = field_one
        self.field_two = field_two


def test_camel_case():
    obj = CamelCase('a', 'b')

    serde_and_compare(obj, true_payload={'fieldOne': 'a', 'fieldTwo': 'b'})
