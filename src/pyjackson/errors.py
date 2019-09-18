class PyjacksonError(Exception):
    """General Pyjackson exception"""
    pass


class DeserializationError(PyjacksonError):
    """Deserialization exception"""
    pass


class SerializationError(PyjacksonError):
    """Serialization exception"""
    pass


class UnserializableError(SerializationError):
    """Raised when unserializable object is being serialized"""
    def __init__(self, obj):
        super(UnserializableError, self).__init__('{} is not serializable'.format(obj))
