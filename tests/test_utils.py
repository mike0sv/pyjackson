from typing import Dict, List, NamedTuple, Tuple, Union

import pytest

from pyjackson.core import Field, Position, Signature, Unserializable
from pyjackson.decorators import as_list, type_field
from pyjackson.errors import PyjacksonError
from pyjackson.generics import StaticSerializer
from pyjackson.utils import (Comparable, flat_dict_repr, get_class_field_names, get_class_fields,
                             get_collection_internal_type, get_function_fields, get_function_signature,
                             get_mapping_types, get_subtype_alias, get_tuple_internal_types, get_type_field_name,
                             has_hierarchy, has_serializer, has_subtype_alias, is_aslist, is_descriptor,
                             is_hierarchy_root, is_init_type_hinted_and_has_correct_attrs, is_serializable,
                             issubclass_safe, resolve_subtype, turn_args_to_kwargs, type_field_position_is, union_args)


def test_flat_dict_repr():
    def func(a, b): pass

    d = {'b': 2, 'a': 1}
    repr = flat_dict_repr(d, None, ', ', False)
    assert repr == 'a=1, b=2' or repr == 'b=2, a=1'
    assert flat_dict_repr(d, func, '; ', True) == '{a=1; b=2}'


def test_is_aslist():
    @as_list
    class AsList:
        pass

    assert is_aslist(AsList)

    class NotAsList:
        pass

    assert not is_aslist(NotAsList)


def test_get_function_fields():
    def func1(a: int, b: str = 'bbb'): pass

    fields1 = get_function_fields(func1)
    assert fields1 == [Field('a', int, False), Field('b', str, True, 'bbb')]

    def func2(a, b='bbb'): pass

    with pytest.raises(PyjacksonError):
        get_function_fields(func2, True)

    fields2 = get_function_fields(func2, False)

    assert fields2 == [Field('a', None, False), Field('b', None, True, 'bbb')]


def test_get_type_field_name():
    @type_field('aaaa')
    class Parent:
        pass

    class Child(Parent):
        pass

    assert get_type_field_name(Parent) == 'aaaa'
    assert get_type_field_name(Child) == 'aaaa'


def test_get_subtype_alias():
    @type_field('aaaa')
    class Parent:
        aaaa = 'parent'

    @as_list
    @type_field('aaaa')
    class AsListParent:
        pass

    assert get_subtype_alias(Parent, {'aaaa': 'parent'}) == 'parent'
    assert get_subtype_alias(AsListParent, ['parent']) == 'parent'


def test_get_function_signature():
    def func(arg: str) -> int: pass

    sig = get_function_signature(func)
    assert sig.args == [Field('arg', str, False)]
    assert sig.output == Field(None, int, False)


def test_get_class_fields():
    class AClass:
        def __init__(self, field1: str, field2: int = 0): pass

    fields = get_class_fields(AClass)

    assert fields == [Field('field1', str, False), Field('field2', int, True, 0)]


def test_get_mapping_types():
    assert get_mapping_types(Dict[str, int]) == (str, int)
    assert get_mapping_types(Dict[str, List[str]]) == (str, List[str])


def test_get_collection_internal_type():
    assert get_collection_internal_type(List[str]) == str
    assert get_collection_internal_type(List[List[str]]) == List[str]


def test_get_class_field_names():
    class AClass:
        def __init__(self, field1: str, field2: int = 0): pass

    fields = get_class_field_names(AClass)

    assert fields == ['field1', 'field2', ]


def test_union_args():
    assert union_args(Union[str, int]) == (str, int)
    assert union_args(Union[List[str], List[int]]) == (List[str], List[int])


def test_turn_args_to_kwargs():
    def func(a, b, c): pass

    args = [1]
    kwargs = {'b': 2, 'c': 3}
    assert turn_args_to_kwargs(func, args, kwargs) == {'a': 1, 'b': 2, 'c': 3}

    class A:
        def meth(self, a, b, c): pass

    assert turn_args_to_kwargs(A.meth, args, kwargs) == {'a': 1, 'b': 2, 'c': 3}


def test_has_subtype_alias():
    @type_field('aaaa')
    class Root:
        pass

    class Child(Root):
        pass

    @as_list
    class AsListRoot:
        pass

    assert has_subtype_alias(Root, {'aaaa': ''})
    assert has_subtype_alias(Child, {'aaaa': ''})
    assert not has_subtype_alias(Root, {'bbbb': ''})
    assert has_subtype_alias(AsListRoot, ['a'])


def test_has_hierarchy():
    @type_field('aaaa')
    class Root:
        pass

    class Child(Root):
        pass

    class NotRoot:
        pass

    assert has_hierarchy(Root)
    assert has_hierarchy(Child)
    assert not has_hierarchy(NotRoot)


def test_issubclass_safe():
    class myint(int):
        pass

    assert issubclass_safe(myint, int)
    assert not issubclass_safe('1', int)
    assert not issubclass_safe('1', '1')


def test_is_descriptor():
    class Descr:
        def __get__(self, instance, owner): pass

    class NotDescr:
        pass

    assert is_descriptor(Descr)
    assert not is_descriptor(NotDescr)


def test_has_serializer():
    class ExternalClass:
        def __init__(self, a):
            self.b = a

    class ExternalSerializer(StaticSerializer):
        real_type = ExternalClass

        @classmethod
        def deserialize(cls, obj: dict) -> object:
            return ExternalClass(obj['c'])

        @classmethod
        def serialize(cls, instance: ExternalClass) -> dict:
            return {'c': instance.b}

    class ExternalNoSerializer:
        def __init__(self, a):
            self.b = a

    assert has_serializer(ExternalClass)
    assert not has_serializer(ExternalNoSerializer)


def test_is_init_type_hinted_and_has_correct_attrs():
    class Good:
        def __init__(self, a: int):
            self.a = a

    class BadNoTypeHints:
        def __init__(self, a):
            self.a = a

    class BadNoAttr:
        def __init__(self, a: int):
            self.b = a

    assert is_init_type_hinted_and_has_correct_attrs(Good(1))
    assert not is_init_type_hinted_and_has_correct_attrs(BadNoTypeHints(1))
    assert not is_init_type_hinted_and_has_correct_attrs(BadNoAttr(1))


def test_is_serializable__init_hints():
    class Ser:
        def __init__(self, a: int):
            self.a = a

    class Unser(Unserializable):
        pass

    assert is_serializable(Ser(1))
    assert not is_serializable(Unser())


def test_is_serializable__external():
    class ExternalClass:
        def __init__(self, a):
            self.b = a

    class ExternalSerializer(StaticSerializer):
        real_type = ExternalClass

        @classmethod
        def deserialize(cls, obj: dict) -> object:
            return ExternalClass(obj['c'])

        @classmethod
        def serialize(cls, instance: ExternalClass) -> dict:
            return {'c': instance.b}

    class ExternalNoSerializer:
        def __init__(self, a):
            self.b = a

    assert is_serializable(ExternalClass(1))
    assert not is_serializable(ExternalNoSerializer(1))


def test_is_serializable__named_tuple():
    ntuple = NamedTuple('ntuple', [('field1', str)])

    assert is_serializable(ntuple('aaa'))

    assert is_serializable(Signature([Field('aaa', int, False)], Field(None, int, False)))


def test_is_serializable__field():
    assert is_serializable(Field('aaa', int, False))


def test_is_hierarchy_root():
    @type_field('aaaa')
    class Root:
        pass

    class Child(Root):
        pass

    class NotRoot:
        pass

    assert is_hierarchy_root(Root)
    assert not is_hierarchy_root(Child)
    assert not is_hierarchy_root(NotRoot)


def test_type_field_position_is():
    @type_field('aaaa', Position.INSIDE)
    class Root:
        pass

    @type_field('aaaa', Position.OUTSIDE)
    class Root2:
        pass

    assert type_field_position_is(Root, Position.INSIDE)
    assert not type_field_position_is(Root, Position.OUTSIDE)
    assert not type_field_position_is(Root2, Position.INSIDE)
    assert type_field_position_is(Root2, Position.OUTSIDE)


def test_resolve_subtype():
    @type_field('aaaa', Position.INSIDE)
    class Root:
        aaaa = 'parent'

    class Child(Root):
        aaaa = 'child'

    assert resolve_subtype(Root, {'aaaa': 'child'}) == Child

    @type_field('aaaa', Position.OUTSIDE)
    class Root2:
        aaaa = 'parent'

    class Child2(Root2):
        aaaa = 'child'

    assert resolve_subtype(Root2, {'aaaa': 'child'}) == Child2


def test_comparable():
    class AClass(Comparable):
        def __init__(self, a: str, b: int):
            self.a = a
            self.b = b

    obj1 = AClass('a', 0)
    obj2 = AClass('a', 0)
    obj3 = AClass('a', 1)

    assert obj1 == obj2
    assert obj1 is not obj2

    assert obj1 != obj3


def test_field():
    def func(a: int, b: str = 'b'): pass

    a, b = get_function_fields(func)
    assert 'a: int' == f'{a}'
    assert 'b: str = b' == f'{b}'


def test_get_tuple_internal_types():
    assert get_tuple_internal_types(Tuple[int]) == (False, (int,))
    assert get_tuple_internal_types(Tuple[int, str]) == (False, (int, str))
    assert get_tuple_internal_types(Tuple[int, ...]) == (True, int)
