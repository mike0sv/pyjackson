import os

import pytest

import pyjackson
from pyjackson.decorators import make_string, type_field
from pyjackson.generics import Serializer
from pyjackson.utils import Comparable, is_generic, issubclass_safe


@type_field('type')
class RootClass:
    type = None


@pytest.fixture
def type_factory():
    def inner(class_name, field_type, base=Comparable):
        @make_string
        class FooType(base):
            def __init__(self, field: field_type):
                self.field = field

        FooType.__name__ = class_name
        return FooType

    return inner


@pytest.fixture
def tmp_file(tmpdir):
    return os.path.join(tmpdir, 'file.txt')


def serde_and_compare(obj, obj_type=None, true_payload=None, check_payload=True):
    if obj_type is None:
        obj_type = type(obj)
        check_subtype = False
        check_instance = True
    else:
        check_subtype = not issubclass_safe(obj_type, Serializer) and not is_generic(obj_type)
        check_instance = False

    payload = pyjackson.serialize(obj, obj_type)
    if true_payload is not None:
        if check_payload:
            assert payload == true_payload
        payload = true_payload
    new_obj = pyjackson.deserialize(payload, obj_type)
    if check_subtype:
        assert issubclass(type(new_obj), obj_type), '{} type must be subtype of {}'.format(new_obj, obj_type)
    elif check_instance:
        assert isinstance(new_obj, obj_type)
    assert obj == new_obj
