import itertools
import sys
from typing import Dict, List

import pytest

from pyjackson import deserialize
from pyjackson.decorators import make_string, type_field
from pyjackson.generics import Serializer, StaticSerializer
from pyjackson.serialization import SerializationError, serialize
from pyjackson.utils import Comparable
from tests.conftest import serde_and_compare


@make_string
class AClass(Comparable):
    def __init__(self, const_list: list):
        self.const_list = const_list


@make_string
class AClassStaticSerializer(StaticSerializer):
    real_type = AClass

    @classmethod
    def deserialize(cls, obj: dict) -> AClass:
        size = obj['size']
        value = obj['value']
        return AClass([value for _ in range(size)])

    @classmethod
    def serialize(cls, instance: AClass) -> object:
        return {'size': len(instance.const_list), 'value': instance.const_list[0] if instance.const_list else None}


class BClass(Comparable):
    def __init__(self, not_typehinted):
        self.not_typehinted = not_typehinted

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<B({})>'.format(self.not_typehinted)


class BSerializer(Serializer):
    real_type = BClass

    def deserialize(self, obj: dict) -> object:
        return BClass(obj)

    def serialize(self, instance: BClass) -> dict:
        return instance.not_typehinted


class BContainer(Comparable):
    def __init__(self, b: BClass):
        self.b = b


class CClass(AClass):
    pass


@make_string
class SizedTestType(Serializer):
    real_type = CClass

    def __init__(self, size: int):
        self.size = size

    def serialize(self, instance: CClass):
        return {'value': instance.const_list[0] if instance.const_list else None}

    def deserialize(self, obj):
        value = obj['value']
        return CClass([value for _ in range(self.size)])


@make_string
class ContainerSized(Comparable):
    def __init__(self, test: SizedTestType(10)):
        self.test = test


class AbstractTestType(Serializer):
    pass


class DClass(AClass):
    pass


@make_string
class ChildSizedTestType(AbstractTestType, Serializer):
    real_type = DClass

    def __init__(self, size: int):
        self.size = size

    def serialize(self, instance: DClass):
        return {'value': instance.const_list[0] if instance.const_list else None}

    def deserialize(self, obj: dict):
        value = obj['value']
        return DClass([value for _ in range(self.size)])


def test_static_serializer():
    @make_string
    class AContainer(Comparable):
        def __init__(self, test: AClass):
            self.test = test

    t1 = AContainer(AClass([5 for _ in range(10)]))

    serde_and_compare(t1)


def test_uninit_serializer():
    o = BClass('a')
    with pytest.raises(SerializationError):
        serialize(o, BSerializer)


def test_b_serializer():
    o = BClass('a')
    as_type = BSerializer()
    serde_and_compare(o, as_type, true_payload='a')


def test_b_container():
    o = BClass('a')
    serde_and_compare(BContainer(o), true_payload={'b': 'a'})


def test_parametrized_serializer():
    payload = {'value': 1}
    obj = deserialize(payload, SizedTestType(5))

    assert [1, 1, 1, 1, 1] == obj.const_list


def test_parametrized():
    t1 = ContainerSized(CClass([5 for _ in range(10)]))

    serde_and_compare(t1, true_payload={'test': {'value': 5}})


def test_serializer_issubclass():
    t1 = ChildSizedTestType
    t2 = ChildSizedTestType(5)
    assert issubclass(t1, AbstractTestType)
    assert issubclass(t1, Serializer)
    assert issubclass(t2, AbstractTestType)
    assert issubclass(t2, Serializer)


def test_parametrized_property():
    with pytest.raises(AttributeError):
        id(SizedTestType.size)

    t1 = SizedTestType(5)
    assert t1.size == 5


_python_version = sys.version_info[:2]


def relations():
    def eq(x, y):
        return x == y

    def type_eq(x, y):
        return type(x) == type(y)

    def is_rel(x, y):
        return x is y

    return [
        eq,
        isinstance,
        issubclass,
        type_eq,
        is_rel
    ]


def create_object_quads():
    pairs = [
        (List, SizedTestType),  # generic type
        (List[str], SizedTestType(2)),  # parametrized generic type
        (list, CClass),  # real type
        (['str'], CClass([1, 1])),  # real instance
        ([1], CClass([1]))  # fake instance
    ]

    skip_python37 = [
        (issubclass, SizedTestType, CClass),  # cant hack TestClass to throw TypeError on subclass check
        (issubclass, SizedTestType(2), CClass),
    ]
    skipping = {(3, 7): skip_python37, (3, 8): skip_python37}

    args = []

    for (r1, o1), (r2, o2) in itertools.combinations(pairs, 2):

        for relation in relations():
            args.append([relation,
                         o1, o2, r1, r2,
                         (relation, o1, o2) in skipping.get(_python_version, [])])
    return args


@pytest.mark.parametrize('relation,o1,o2,ref1,ref2,skip', create_object_quads())
def test_relation(relation, o1, o2, ref1, ref2, skip: bool):
    if skip:
        pytest.skip('skip {} {} {} for python {}'.format(relation, o1, o2, _python_version))
        return
    exception = None
    try:
        result = relation(ref1, ref2)
    except Exception as e:
        result = None
        exception = e

    if exception is None:
        try:
            rel = relation(o1, o2)
        except Exception as e2:
            msg = '{}({}, {}) must not throw exception "{}: {}" like {}({}, {})={}'.format(
                relation.__name__,
                o1, o2, type(e2).__name__, e2, relation.__name__,
                ref1, ref2, result)
            raise Exception(msg)
        msg = '{}({}, {})={} must be {}: {}({}, {})={}'.format(relation.__name__, o1, o2, rel,
                                                               result, relation.__name__, ref1,
                                                               ref2, result)
        assert rel == result, msg
    else:
        msg = '\n{}({}, {}) should raise\n"{}: {}"\n like {}({}, {})'.format(
            relation.__name__, o1, o2,
            type(exception).__name__, exception,
            relation.__name__, ref1, ref2)
        with pytest.raises(type(exception)):
            relation(o1, o2)
            pytest.fail(msg)


def test_primitive_serializer():
    @type_field('type')
    class Root(Serializer):
        pass

    class PrimitiveDatasetType(Root):
        type = 'primitive'

        def __init__(self, ptype: str):
            self.ptype = ptype

        @property
        def to_type(self):
            import builtins
            return getattr(builtins, self.ptype)

        def deserialize(self, obj):
            return self.to_type(obj)

        def serialize(self, instance):
            return instance

    IntSerializer = PrimitiveDatasetType('int')

    serde_and_compare(1, IntSerializer)


def test_dict_keys():
    class IntDict(Comparable):
        def __init__(self, d: Dict[int, int]):
            self.d = d

    serde_and_compare(IntDict({1: 1}))
