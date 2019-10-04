from typing import Set

from pyjackson import serialize
from pyjackson.core import Comparable
from pyjackson.decorators import make_string
from tests.conftest import serde_and_compare


@make_string
class AClass(Comparable):
    def __init__(self, value: str):
        self.value = value

    def __hash__(self):
        return hash(self.value)


def test_set():
    value = {AClass('a'), AClass('b')}
    serde_and_compare(value, Set[AClass])
    assert serialize(value, Set[AClass]) in [[{'value': 'a'}, {'value': 'b'}],
                                             [{'value': 'b'}, {'value': 'a'}]]


def test_set_hint():
    @make_string
    class CClass(Comparable):
        def __init__(self, value: Set[str]):
            self.value = value

    value = CClass({'a', 'b'})
    serde_and_compare(value)
    assert serialize(value) in [
        {'value': ['a', 'b']},
        {'value': ['b', 'a']}
    ]
