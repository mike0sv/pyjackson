import uuid

import pytest

from pyjackson.serialization import SerializationError, serialize
from tests.conftest import serde_and_compare


def test_uuid(type_factory):
    Foo = type_factory('Foo', uuid.UUID)
    foo = Foo(uuid.uuid4())
    serde_and_compare(foo, Foo)


@pytest.mark.parametrize('obj', [1, 1., 1j, 'str', True])
def test_primitive_type(obj, type_factory):
    Foo = type_factory('Foo', type)

    serde_and_compare(Foo(type(obj)), Foo)


def test_primitive_type_raises(type_factory):
    Foo = type_factory('Foo', type)

    with pytest.raises(SerializationError):
        serialize(Foo(Foo))
