import builtins
import datetime
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


class DatetimeSerializer(StaticSerializer):
    """:class:`~pyjackson.generics.StaticSerializer` for :class:`datetime.datetime` type"""
    real_type = datetime.datetime
    DT_FORMAT = '%Y-%m-%d %H:%M:%S.%f %z'

    @classmethod
    def deserialize(cls, obj: str):
        tz = obj.split(' ')[-1]
        if tz != '':
            return datetime.datetime.strptime(obj, cls.DT_FORMAT)
        else:
            return datetime.datetime.strptime(obj, cls.DT_FORMAT.rstrip('%z'))

    @classmethod
    def serialize(cls, instance: datetime.datetime):
        return instance.strftime(cls.DT_FORMAT)
