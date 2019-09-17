import builtins
import uuid

from pyjackson.generics import StaticSerializer


class PrimitiveTypeSerializer(StaticSerializer):
    real_type = type
    _PRIMITIVES = {int, str, bool, complex, float}

    @classmethod
    def deserialize(cls, obj: str):
        return getattr(builtins, obj)

    @classmethod
    def serialize(cls, instance):
        if instance not in PrimitiveTypeSerializer._PRIMITIVES:
            raise ValueError("Cannot serialize {} as primitive".format(instance))
        return str(instance)


class UuidSerializer(StaticSerializer):
    real_type = uuid.UUID

    @classmethod
    def deserialize(cls, obj: str):
        return uuid.UUID(obj)

    @classmethod
    def serialize(cls, instance):
        return str(instance)
