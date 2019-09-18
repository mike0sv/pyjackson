import builtins
import uuid

from pyjackson.generics import StaticSerializer
from pyjackson.serialization import SerializationError


class PrimitiveTypeSerializer(StaticSerializer):
    """:class:`~pyjackson.generics.StaticSerializer` for primitive types"""
    real_type = type
    _PRIMITIVES = {int, str, bool, complex, float}

    @classmethod
    def deserialize(cls, obj: str):
        return getattr(builtins, obj)

    @classmethod
    def serialize(cls, instance):
        if instance not in PrimitiveTypeSerializer._PRIMITIVES:
            raise SerializationError("Cannot serialize {} as primitive".format(instance))
        return instance.__name__


class UuidSerializer(StaticSerializer):
    """:class:`~pyjackson.generics.StaticSerializer` for :class:`uuid.UUID` type"""
    real_type = uuid.UUID

    @classmethod
    def deserialize(cls, obj: str):
        return uuid.UUID(obj)

    @classmethod
    def serialize(cls, instance):
        return str(instance)
