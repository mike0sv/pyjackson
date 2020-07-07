from typing import Dict, Set, Type, Union, no_type_check

from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from pyjackson.core import BUILTIN_TYPES, TYPE_FIELD_NAME_FIELD_NAME
from pyjackson.utils import (get_class_fields, get_generic_origin, is_generic_or_union, is_hierarchy_root,
                             is_init_type_hinted, is_union, union_args)


def _new_model(type_, name=None, nested=False, polymorphism=False):
    name = name or f'{type_.__name__}Model'
    return type(name, (PyjacksonModel,), {'__type__': type_,
                                          '__autogen_nested__': nested,
                                          '__allow_polymorphism__': polymorphism})


def _substitute_generics(type_, polymorphism):
    new_types = tuple(_substitute_nested_type(t, polymorphism) for t in type_.__args__)
    return get_generic_origin(type_)[new_types]


def _substitute_nested_type(type_, polymorphism):
    if type_ in BUILTIN_TYPES or (not is_generic_or_union(type_) and not is_init_type_hinted(type_)):
        return type_
    if is_generic_or_union(type_):
        return _substitute_generics(type_, polymorphism)

    return _new_model(type_, nested=True, polymorphism=polymorphism)


def _make_not_optional(type_):
    none_type = type(None)
    if not is_union(type_) or none_type not in union_args(type_):
        return type_
    return Union[tuple(t for t in union_args(type_) if t is not none_type)]


class PyjacksonModelMetaclass(ModelMetaclass):
    __root__ = None

    @no_type_check
    def __new__(mcs, name, bases, namespace, **kwargs):
        if kwargs.get('__base_definition__', False):
            kwargs.pop('__base_definition__')
            mcs.__root__ = super().__new__(mcs, name, bases, namespace, **kwargs)
            return mcs.__root__
        __type__ = namespace.pop('__type__', None)
        if __type__ is None or not isinstance(__type__, type):
            raise ValueError(f'__type__ field is be set to type for {name}')

        fields = get_class_fields(__type__)
        include = set(namespace.pop('__include__', set(f.name for f in fields)))
        exclude = set(namespace.pop('__exclude__', set()))
        force_required = set(namespace.pop('__force_required__', set()))
        autogen_nested = namespace.pop('__autogen_nested__', False)
        allow_polymorphism = namespace.pop('__allow_polymorphism__', False)
        subtype_models: Dict[str, Type[BaseModel]] = namespace.pop('__subtype_models__', {})

        annotations = namespace.get('__annotations__', {})
        for field in fields:
            name = field.name
            if name in exclude or name not in include:
                continue
            if field.has_default and name not in namespace:
                namespace[name] = field.default
            if name not in annotations:
                field_type = field.type
                if autogen_nested:
                    field_type = _substitute_nested_type(field_type, allow_polymorphism)
                annotations[name] = field_type
            if name in force_required:
                del namespace[name]
                annotations[name] = _make_not_optional(annotations[name])

        if allow_polymorphism and is_hierarchy_root(__type__):
            field_type_field = getattr(__type__, TYPE_FIELD_NAME_FIELD_NAME)
            annotations[field_type_field] = str

            def validate(cls: Type[BaseModel], value):
                if isinstance(value, dict) and field_type_field in value:
                    _subtype_name = value.pop(field_type_field)
                    _subtype = __type__._subtypes[_subtype_name]
                    if _subtype_name not in subtype_models:
                        subtype_models[_subtype_name] = _new_model(_subtype,
                                                                   nested=autogen_nested,
                                                                   polymorphism=allow_polymorphism)
                    child_model = subtype_models[_subtype_name]
                    return child_model.validate(value)
                return super(cls).validate(value)

            namespace['validate'] = classmethod(validate)
        namespace['__annotations__'] = annotations
        new = super().__new__(mcs, name, bases, namespace, **kwargs)
        new.__type__ = __type__
        return new


class PyjacksonModel(BaseModel, metaclass=PyjacksonModelMetaclass, __base_definition__=True):
    __type__: type = None
    __force_required__: Set[str] = None
    __exclude__: Set[str] = None
    __include__: Set[str] = None
    __autogen_nested__ = False
    __allow_polymorphism__ = False
    __subtype_models__: Dict[str, Type[BaseModel]] = {}

    @classmethod
    def from_data(cls, data):
        model = cls.validate(data)
        return model.dict()

    def dict(self, **kwargs):
        d = super(PyjacksonModel, self).dict(**kwargs)
        return self.__type__(**d)
