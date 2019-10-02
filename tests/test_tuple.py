from typing import Tuple

from pyjackson.core import Comparable
from pyjackson.decorators import make_string
from tests.conftest import serde_and_compare


@make_string
class AClass(Comparable):
    def __init__(self, value: str):
        self.value = value


@make_string
class BClass(Comparable):
    def __init__(self, value: int):
        self.value = value


def test_typed_tuple():
    serde_and_compare((AClass('a'), BClass(1)), Tuple[AClass, BClass], [{'value': 'a'}, {'value': 1}])


def test_typed_tuple_hint():
    @make_string
    class CClass(Comparable):
        def __init__(self, value: Tuple[str, int]):
            self.value = value

    serde_and_compare(CClass(('a', 1)), true_payload={'value': ['a', 1]})


def test_unsized_tuple():
    serde_and_compare((1, 2, 3), Tuple[int, ...], [1, 2, 3])


def test_unsized_tuple_hint():
    @make_string
    class CClass(Comparable):
        def __init__(self, value: Tuple[int, ...]):
            self.value = value

    serde_and_compare(CClass((3, 2)), true_payload={'value': [3, 2]})
