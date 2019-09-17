import uuid

from pyjackson.comparable import Comparable
from pyjackson.utils import make_string
from tests.conftest import serde_and_compare


@make_string
class Foo(Comparable):
    def __init__(self, bar: uuid.UUID):
        self.bar = bar


def test_uuid():
    foo = Foo(uuid.uuid4())
    serde_and_compare(foo, Foo)
