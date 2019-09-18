from typing import Iterable, Optional, Tuple

import pytest

from pyjackson import deserialize, serialize
from pyjackson.generics import Serializer
from pyjackson.utils import Comparable


class MockNumpyNdarray:
    def __init__(self, data):
        self.data = data
        self.dtype = self._get_dtype(data)
        self.shape = self._get_shape(data)

    def _get_dtype(self, data):
        if isinstance(data, Iterable):
            subtypes = set(self._get_dtype(d) for d in data)
            assert len(subtypes) == 1, 'inconsistent array types {}'.format(subtypes)
            return next(iter(subtypes))
        else:
            return type(data)

    def _get_shape(self, data) -> tuple:
        size = (len(data),)
        if isinstance(data[0], Iterable):
            assert len(set(len(d) for d in data)) == 1, 'inconsistent array sizes'
            size = size + self._get_shape(data[0])
        return size

    def __eq__(self, other):
        return isinstance(other, MockNumpyNdarray) and all(getattr(self, a) == getattr(other, a) for a in [
            'data', 'shape', 'dtype'
        ])


class MockNdarraySerializer(Serializer):
    real_type = MockNumpyNdarray

    def __init__(self, shape: Tuple[Optional[int], ...], dtype: type):
        self.dtype = dtype
        self.shape = shape

    def deserialize(self, obj):
        a = MockNumpyNdarray(obj)
        assert a.dtype == self.dtype
        assert all(s == o for o, s in zip(a.shape, self.shape) if s is not None)
        return a

    def serialize(self, instance: MockNumpyNdarray):
        return instance.data


class SizedArrayContainer(Comparable):
    def __init__(self, arr: MockNdarraySerializer((3,), int)):
        self.arr = arr


class MultidimArrayContainer(Comparable):
    def __init__(self, arr: MockNdarraySerializer((2, 3), int)):
        self.arr = arr


class MultidimUnsizedArrayContainer(Comparable):
    def __init__(self, arr: MockNdarraySerializer((None, 2), int)):
        self.arr = arr


def test_sized():
    real_data = [1, 2, 3]
    ext_type = MockNumpyNdarray(real_data)
    c = SizedArrayContainer(ext_type)
    ser = serialize(c)

    assert real_data == ser['arr']

    deser = deserialize(ser, SizedArrayContainer)

    assert deser == c


def test_multidim():
    real_data = [
        [1, 2, 3],
        [4, 5, 6]
    ]
    ext_type = MockNumpyNdarray(real_data)
    c = MultidimArrayContainer(ext_type)
    ser = serialize(c)

    assert real_data == ser['arr']

    deser = deserialize(ser, MultidimArrayContainer)

    assert deser == c


@pytest.mark.parametrize('times', [1, 2, 3])
def test_unsized(times):
    real_data = [[1, 2] for _ in range(times)]

    array = MockNumpyNdarray(real_data)
    container = MultidimUnsizedArrayContainer(array)
    ser = serialize(container)
    assert real_data == ser['arr']
    new_container = deserialize(ser, MultidimUnsizedArrayContainer)
    assert new_container == container
