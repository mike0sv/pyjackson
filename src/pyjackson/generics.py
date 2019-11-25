import inspect
import sys
from abc import abstractmethod
from functools import lru_cache, wraps
from typing import Hashable, Type, Union

from pyjackson.core import TYPE_FIELD_NAME_FIELD_NAME
from pyjackson.utils import flat_dict_repr, is_descriptor, turn_args_to_kwargs

SERIALIZER_MAPPING = dict()

_pv_major, _pv_minor = sys.version_info[:2]


def _register_serializer(cls, real_type):
    """Register cls as serializer for real_type"""
    if real_type is not None:
        if isinstance(real_type, Hashable) and real_type != list and real_type != dict:
            SERIALIZER_MAPPING[real_type] = cls


class _SerializerMetaMeta(type):
    """Metaclass for :class:`_SerializerMeta`

    Mostly needed to support correct isinstance, issubclass and == behaviour in some cases
    """

    def __eq__(self, other):
        if issubclass(other, self) and other._is_dynamic:
            return True
        return super(_SerializerMetaMeta, self).__eq__(other)

    def __hash__(self):
        return hash(self.__name__)

    def __subclasscheck__(self, subclass):
        return super(_SerializerMetaMeta, self).__subclasscheck__(subclass)

    def __instancecheck__(self, instance):
        return super(_SerializerMetaMeta, self).__instancecheck__(instance)

    @property
    def _is_dynamic(cls):
        return getattr(cls, '_dynamic', False)


class _SerializerMeta(type, metaclass=_SerializerMetaMeta):
    """
    Metaclass for :class:`Serializer`

    Adds serializer's real_type as it's base class and implements custom type and comparison logic.
    It is needed to support correct isinstance, issubclass and == behaviour in some cases.
    """

    def __new__(mcs, name, bases, namespace):
        real_type = namespace.get('real_type')
        if real_type is not None and real_type not in bases:
            bases = bases + (real_type,)
        return super(_SerializerMeta, mcs).__new__(mcs, name, bases, namespace)

    def __hash__(self):
        return hash(self.__name__)

    def __eq__(self, other):
        if other is self._metaclass:
            return True
        if isinstance(other, _SerializerMeta) and (self._is_dynamic and
                                                   other._is_dynamic) and self._class is other._class:
            return all(getattr(self, f) == getattr(other, f) for f in self._fields)
        return super(_SerializerMeta, self).__eq__(other)

    def __subclasscheck__(self, subclass):
        if self._is_dynamic:
            raise TypeError('Parameterized generics cannot be used with class or instance checks')
        if self.real_type is not None and self.real_type == subclass:
            return True
        return super(_SerializerMeta, self).__subclasscheck__(subclass)

    def __instancecheck__(self, instance):
        if self._is_dynamic:
            raise TypeError('Parameterized generics cannot be used with class or instance checks')
        if self.real_type is not None and isinstance(instance, self.real_type):
            return True
        return super(_SerializerMeta, self).__instancecheck__(instance)

    @property
    def _is_dynamic(cls):
        return getattr(cls, '_dynamic', False)

    @property
    def _metaclass(cls):
        return getattr(cls, '_parent_metaclass', type(cls))

    @property
    def _class(cls):
        return getattr(cls, '_parent_class', cls)

    @property
    def _fields(cls):
        return getattr(cls, '_init_args', tuple())


def _type_cache(func):
    cached = lru_cache(None)(func)

    @wraps(func)
    def inner(cls, *args, **kwargs):
        kwargs = turn_args_to_kwargs(cls.__init__, args, kwargs)
        try:
            return cached(cls, **kwargs)
        except TypeError:
            pass  # All real errors (not unhashable args) are raised below.
        return func(cls, **kwargs)

    return inner


def _get_defining_class(cls, method, method_name=None, mro=None, stop_class=None):
    mro = mro or inspect.getmro(cls)
    method_name = method_name or method.__name__
    for parent in mro:
        m = parent.__dict__.get(method_name)
        if m is not None and (m is method or getattr(m, '__func__', None) is method):
            return parent
        if stop_class is not None and parent is stop_class:
            return stop_class


class _class_no_data_descriptor:
    def __init__(self, cls, no_data_descriptor):
        self.cls = cls
        self.no_data_descriptor = no_data_descriptor

    def __get__(self, instance, owner):
        if instance is not None:
            raise AttributeError('You must have been initialized generic type {}. Don\'t do that ;)'.format(self.cls))
        return self.no_data_descriptor.__get__(owner, owner)


def _transform_to_class_methods(cls):
    metaclass = type(cls)
    mro = inspect.getmro(cls)
    ignore = {'__class__', '__dict__', '__bases__', '__name__', '__qualname__',
              '__mro__', '__subclasses__', '__init_subclass__', '__subclasshook__',
              '__instancecheck__', '__subclasscheck__', '__weakref__',
              '__new__', '__init__', '__getattribute__', '__setattr__',
              '__eq__'}
    metaclass_attrs = {}
    class_attrs = {}
    for name in dir(cls):
        if name in ignore:
            continue
        attr = getattr(cls, name)
        if callable(attr):
            if isinstance(attr, type):
                continue
            if inspect.ismethod(attr):
                # skip static and class methods
                # unbound methods are not methods, they are functions
                continue
            defining_class = _get_defining_class(cls, attr, name, mro, cls.real_type)
            if defining_class is cls.real_type:
                continue

            if name.startswith('__'):
                metaclass_attrs[name] = attr
            elif isinstance(defining_class.__dict__[name], staticmethod):
                class_attrs[name] = attr
            else:
                class_attrs[name] = classmethod(attr)
        elif inspect.isdatadescriptor(attr):
            metaclass_attrs[name] = attr
        elif is_descriptor(attr):
            class_attrs[name] = _class_no_data_descriptor(cls, attr)

    for name, attr in class_attrs.items():
        setattr(cls, name, attr)

    for name, attr in metaclass_attrs.items():
        setattr(metaclass, name, attr)


class Serializer(metaclass=_SerializerMeta):
    """
    A base for defining custom serializers.
    # TODO definitely more docs here
    """
    real_type = None  # type: Type

    @_type_cache
    def __new__(cls, **kwargs):
        has_init = issubclass(_get_defining_class(cls, cls.__init__), Serializer)
        if getattr(cls, '_dynamic', False):
            if has_init:
                cls.__init__(cls, **kwargs)
            _transform_to_class_methods(cls)
            return cls
        if has_init:
            kwargs_str = flat_dict_repr(kwargs, func_order=cls.__init__)
        else:
            kwargs_str = ''

        metaclass = type(cls)
        metaclass_name = '{}Metaclass[{}]'.format(cls.__name__, kwargs_str)
        new_metaclass = type(metaclass_name, (metaclass,), {'_dynamic': True, '_parent_metaclass': metaclass})

        type_name = '{}[{}]'.format(cls.__name__, kwargs_str)
        __dict__ = {'_dynamic': True, '_parent_class': cls, '_init_args': tuple(kwargs.keys())}
        if hasattr(cls, TYPE_FIELD_NAME_FIELD_NAME):
            type_field_name = getattr(cls, TYPE_FIELD_NAME_FIELD_NAME)
            type_field_value = getattr(cls, type_field_name)
            __dict__[type_field_name] = type_field_value
        new_type = new_metaclass(type_name, (cls,), __dict__)
        instance = new_type(**kwargs)
        return instance

    @abstractmethod
    def deserialize(self, obj: dict) -> object:
        pass

    @abstractmethod
    def serialize(self, instance: object) -> dict:
        pass

    def __init_subclass__(cls, **kwargs):
        super(Serializer, cls).__init_subclass__(**kwargs)
        _register_serializer(cls, cls.real_type)

    def __eq__(self, other):
        if isinstance(other, _SerializerMeta):
            return False
        print('lolo' * 10)
        return super().__eq__(other)

    def __subclasscheck__(self, subclass):
        raise TypeError('Parameterized generics cannot be used with class or instance checks')

    def __instancecheck__(self, instance):
        raise TypeError('Parameterized generics cannot be used with class or instance checks')

    # TODO def validate(self, obj):


class StaticSerializer(Serializer):
    """
    An easier way to define a serializer if it has no 'generic' arguments.
    """

    @classmethod
    @abstractmethod
    def deserialize(cls, obj: dict) -> object:
        pass

    @classmethod
    @abstractmethod
    def serialize(cls, instance: object) -> dict:
        pass


SerializerType = Union[Type, Serializer]
