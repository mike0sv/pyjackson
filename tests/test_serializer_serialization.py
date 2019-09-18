import sys

from pyjackson import serialize
from pyjackson.decorators import make_string, type_field
from pyjackson.deserialization import deserialize
from pyjackson.generics import Serializer
from pyjackson.utils import Comparable

_python_version = sys.version_info[:2]


@make_string('const_list', include_name=True)
class AClass:
    def __init__(self, const_list: list):
        self.const_list = const_list


class SizedTestType(Comparable, Serializer):
    real_type = AClass

    def __init__(self, size: int):
        self.size = size

    def serialize(self, instance: AClass):
        return {'value': instance.const_list[0] if instance.const_list else None}

    def deserialize(self, obj): pass


@type_field('type')
class AbstractType(Serializer):
    pass


class ChildGenericType(AbstractType, Comparable):
    real_type = AClass
    type = 'child'

    def __init__(self, size: int):
        self.size = size

    def serialize(self, instance: AClass):
        return {'value': instance.const_list[0] if instance.const_list else None}

    def deserialize(self, obj): pass


class GenericTypeHolder(Comparable):
    def __init__(self, gen_type: AbstractType):
        self.gen_type = gen_type


def test_use_as_type_hint():
    def func(arg: SizedTestType(10)): pass

    id(func.__annotations__)


def test_generic_serde():
    gen = SizedTestType(10)

    payload = serialize(gen)
    assert payload == {'size': 10}
    new_gen = deserialize(payload, SizedTestType)
    assert issubclass(new_gen, SizedTestType)
    assert new_gen.size == 10

    obj = AClass([1 for _ in range(10)])
    assert serialize(obj, gen) == serialize(obj, new_gen)


def test_hierarchy_serde():
    gen = ChildGenericType(10)

    payload = serialize(gen)
    assert payload == {'size': 10, 'type': 'child'}

    new_gen = deserialize(payload, AbstractType)
    assert issubclass(new_gen, ChildGenericType)
    assert new_gen.size == 10

    obj = AClass([1 for _ in range(10)])
    assert serialize(obj, gen) == serialize(obj, new_gen)


def test_inner_hierarchy_serde():
    holder = GenericTypeHolder(ChildGenericType(15))

    payload = serialize(holder)

    assert payload == {'gen_type': {'type': 'child', 'size': 15}}

    new_holder = deserialize(payload, GenericTypeHolder)

    assert holder == new_holder
