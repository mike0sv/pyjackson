from pyjackson.decorators import cached_property
from pyjackson.generics import Serializer
from tests.conftest import serde_and_compare


class NonDataDescriptor:
    def __get__(self, instance: 'ASerializer', owner):
        if instance is None:
            return self
        return instance.add


class ASerializer(Serializer):
    def __init__(self, add: str):
        self.add = add
        self.temp_field = None

    def helper_method(self, field):
        self.temp_field = field

    def deserialize(self, obj: dict) -> object:
        self.helper_method(obj)
        return self.temp_field[:-len(self.add)]

    def serialize(self, instance: object) -> dict:
        self.helper_method(instance)
        return self.temp_field + self.add

    def __add__(self, other):
        return ASerializer(self.add + other.add)

    @property
    def a_property(self):
        return self.add * 2

    @cached_property
    def c_property(self):
        return self.add * 3

    no_data_descriptor = NonDataDescriptor()


def test_serializer_type_cache():
    type1 = ASerializer('a')
    type2 = ASerializer('a')
    type3 = ASerializer(add='a')
    type4 = ASerializer('b')

    assert type1 is type2
    assert type1 is type3
    assert type1 is not type4


def test_serializer_logic():
    serde_and_compare('a', ASerializer('b'), 'ab')


def test_serializer_logic_add():
    ser1 = ASerializer('a')
    ser2 = ASerializer('b')
    sum_ser = ser1 + ser2

    serde_and_compare('', sum_ser, 'ab')


def test_serializer_property():
    ser1 = ASerializer('a')

    assert ser1.a_property == 'aa'


def test_serializer_cached_property():
    ser1 = ASerializer('a')

    assert ser1.c_property == 'aaa'


def test_non_data_descriptor():
    ser1 = ASerializer('a')

    assert ser1.no_data_descriptor == 'a'


def test_instance_class_and_static_method_access():
    class MySerializer(Serializer):
        def method(self):
            return self.clsmethod('a') + self.sttcmethod('b')

        @classmethod
        def clsmethod(cls, arg1):
            return arg1

        @staticmethod
        def sttcmethod(arg1):
            return arg1

    obj = MySerializer()
    assert obj.method() == 'ab'
