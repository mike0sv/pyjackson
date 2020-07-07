from typing import List, Optional, Union

import pytest
from pydantic import ValidationError

from pyjackson.decorators import type_field
from pyjackson.pydantic_ext import PyjacksonModel, _make_not_optional


class PClass:
    def __init__(self, field1: str, field2: int = 0):
        self.field1 = field1
        self.field2 = field2


class PClassModel(PyjacksonModel):
    __type__ = PClass


class PNested:
    def __init__(self, a: str, c: List[PClass]):
        self.a = a
        self.c = c


def test_no_type():
    with pytest.raises(ValueError):
        class Model(PyjacksonModel):
            pass


def test_validation():
    model = PClassModel.validate({'field1': 'a', 'field2': 1})
    assert model.field1 == 'a'
    assert model.field2 == 1

    with pytest.raises(ValidationError):
        PClassModel.validate({'field2': 3})


def test_override():
    class PClassModelOR(PyjacksonModel):
        __type__ = PClass
        field1 = 'b'
        field2: list

    model = PClassModelOR.validate({'field2': []})
    assert model.field1 == 'b'
    assert model.field2 == []

    with pytest.raises(ValidationError):
        PClassModelOR.validate({'field2': 3})


def test_validation_nested():
    class PNestedModel(PyjacksonModel):
        __type__ = PNested
        c: List[PClassModel]

    model = PNestedModel.validate({'a': 'a', 'c': [{'field1': 'a', 'field2': 1}]})
    assert model.a == 'a'
    assert isinstance(model.c, list)
    assert len(model.c) == 1
    c = model.c[0]
    assert isinstance(c, PClassModel)
    assert c.field1 == 'a'
    assert c.field2 == 1

    with pytest.raises(ValidationError):
        PNestedModel.validate({'a': 'a'})


def test_from_data():
    obj = PClassModel.from_data({'field1': 'a', 'field2': 1})
    assert isinstance(obj, PClass)
    assert obj.field1 == 'a'
    assert obj.field2 == 1

    with pytest.raises(ValidationError):
        PClassModel.from_data({'field2': 2})


def test_from_data_nested():
    class PNestedModel(PyjacksonModel):
        __type__ = PNested
        c: List[PClassModel]

    obj = PNestedModel.from_data({'a': 'b', 'c': [{'field1': 'a', 'field2': 1}]})
    assert isinstance(obj, PNested)
    assert obj.a == 'b'

    assert isinstance(obj.c, list)
    assert len(obj.c) == 1
    c = obj.c[0]

    assert isinstance(c, PClass)
    assert c.field1 == 'a'
    assert c.field2 == 1

    with pytest.raises(ValidationError):
        PNestedModel.from_data({'a': 'a'})


def test_int_conversion():
    with pytest.raises(ValidationError):
        PClassModel.from_data({'field1': 'a', 'field2': 'b'})


def test_include():
    class PModelInclude(PyjacksonModel):
        __type__ = PClass
        __include__ = {'field1'}

        class Config:
            extra = 'forbid'

    obj = PModelInclude.from_data({'field1': 'a'})
    assert isinstance(obj, PClass)
    assert obj.field1 == 'a'
    assert obj.field2 == 0

    with pytest.raises(ValidationError):
        p = PModelInclude.from_data({'field1': 'a', 'field2': 1})
        print(p)


def test_exclude():
    class PModelExclude(PyjacksonModel):
        __type__ = PClass
        __exclude__ = {'field2'}

        class Config:
            extra = 'forbid'

    obj = PModelExclude.from_data({'field1': 'a'})
    assert isinstance(obj, PClass)
    assert obj.field1 == 'a'
    assert obj.field2 == 0

    with pytest.raises(ValidationError):
        PModelExclude.from_data({'field1': 'a', 'field2': 1})


def test_force_required():
    class PModelReq(PyjacksonModel):
        __type__ = PClass
        __force_required__ = {'field2'}

    obj = PModelReq.from_data({'field1': 'a', 'field2': 1})
    assert isinstance(obj, PClass)
    assert obj.field1 == 'a'
    assert obj.field2 == 1

    with pytest.raises(ValidationError):
        PModelReq.from_data({'field1': 'a'})


def test_force_required_with_default():
    class AClass:
        def __init__(self, field: int = None):
            self.field = field

    class AModel(PyjacksonModel):
        __type__ = AClass
        __force_required__ = ['field']

    data = {'field': 1}
    obj = AModel.from_data(data)
    assert isinstance(obj, AClass)
    assert obj.field == 1

    with pytest.raises(ValidationError):
        AModel.from_data({})


def test_poymorphism_auto():
    @type_field('type')
    class Root:
        pass

    class B(Root):
        def __init__(self, b: str):
            self.b = b

    class C(Root):
        def __init__(self, c: int):
            self.c = c

    class RootModel(PyjacksonModel):
        __type__ = Root
        __allow_polymorphism__ = True

    b = RootModel.from_data({'type': B.type, 'b': 'b'})
    assert isinstance(b, B)
    assert b.b == 'b'

    c = RootModel.from_data({'type': C.type, 'c': 1})
    assert isinstance(c, C)
    assert c.c == 1


def test_poymorphism_route():
    @type_field('type')
    class Root:
        pass

    class B(Root):
        def __init__(self, b: str):
            self.b = b

    class BModel(PyjacksonModel):
        __type__ = B
        b = 'a'

    class RootModel(PyjacksonModel):
        __type__ = Root
        __allow_polymorphism__ = True
        __subtype_models__ = {B.type: BModel}

    b = RootModel.from_data({'type': B.type})
    assert isinstance(b, B)
    assert b.b == 'a'


def test_autogen_nested():
    class B:
        def __init__(self, b: str):
            self.b = b

    class A:
        def __init__(self, a: List[B]):
            self.a = a

    class AM(PyjacksonModel):
        __type__ = A
        __autogen_nested__ = True

    obj = AM.from_data({'a': [{'b': 'c'}]})
    assert isinstance(obj, A)
    assert isinstance(obj.a, list)
    assert len(obj.a) == 1
    a = obj.a[0]
    assert isinstance(a, B)
    assert a.b == 'c'


class AForwardRef:
    def __init__(self, a: List['BForwardRef']):
        self.a = a


class BForwardRef:
    def __init__(self, b: str):
        self.b = b


def test_autogen_nested_forward_ref():
    class AM(PyjacksonModel):
        __type__ = AForwardRef
        __autogen_nested__ = True

    obj = AM.from_data({'a': [{'b': 'c'}]})
    assert isinstance(obj, AForwardRef)
    assert isinstance(obj.a, list)
    assert len(obj.a) == 1
    a = obj.a[0]
    assert isinstance(a, BForwardRef)
    assert a.b == 'c'


def test_autogen_nested_with_polymorphism():
    @type_field('type')
    class Root:
        pass

    class B(Root):
        def __init__(self, b: str):
            self.b = b

    class C(Root):
        def __init__(self, c: int):
            self.c = c

    class A:
        def __init__(self, a: List[Root]):
            self.a = a

    class AM(PyjacksonModel):
        __type__ = A
        __autogen_nested__ = True
        __allow_polymorphism__ = True

    obj = AM.from_data({'a': [{'type': B.type, 'b': 'c'}, {'type': C.type, 'c': 5}]})
    assert isinstance(obj, A)
    assert isinstance(obj.a, list)
    assert len(obj.a) == 2
    b, c = obj.a
    assert isinstance(b, B)
    assert b.b == 'c'

    assert isinstance(c, C)
    assert c.c == 5


def test_autogen_nested_union():
    class B:
        def __init__(self, b: str):
            self.b = b

    class A:
        def __init__(self, a: Union[B, str]):
            self.a = a

    class AM(PyjacksonModel):
        __type__ = A
        __autogen_nested__ = True

    obj = AM.from_data({'a': {'b': 'c'}})
    assert isinstance(obj, A)
    assert isinstance(obj.a, B)
    assert obj.a.b == 'c'


def test_make_not_optional():
    assert _make_not_optional(int) == int
    assert _make_not_optional(Optional[str]) == str
    assert _make_not_optional(Union[int, str]) == Union[int, str]
    assert _make_not_optional(Union[int, str, None]) == Union[int, str]
