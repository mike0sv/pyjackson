import json
from typing import Type, TypeVar

from .deserialization import deserialize
from .serialization import serialize


def loads(payload: str, as_class: type):
    """
    Deserialize `payload` to `as_class` instance

    :param payload: JSON string
    :param as_class: type or serializer
    :return: deserialized instance of as_class (or real_type of serializer)
    """
    obj = json.loads(payload)
    return deserialize(obj, as_class)


def load(fp, as_class: type):
    """
    Deserialize content of file-like `fp` to `as_class` instance

    :param fp: file-like object to read
    :param as_class: type or serializer
    :return: deserialized instance of as_class (or real_type of serializer)
    """
    return loads(fp.read(), as_class)


def dumps(obj, as_class: type = None):
    """
    Serialize obj to JSON string as `as_class`

    :param obj: object to serialize
    :param as_class: type or serializer
    :return: JSON string representation
    """
    payload = serialize(obj, as_class)
    return json.dumps(payload)


def dump(fp, obj, as_class: type = None):
    """
    Serialize obj to JSON as `as_class` and write it to file-like `fp`

    :param fp: file-like object to write
    :param obj: object to serialize
    :param as_class: type or serializer
    :return: bytes written
    """
    return fp.write(dumps(obj, as_class))


T = TypeVar('T')


def read(path: str, as_class: Type[T]) -> T:
    """
    Deserialize object from file in `path` as as_class

    :param path: path to file with JSON representation
    :param as_class: type or serializer
    :return: deserialized instance of as_class (or real_type of serializer)
    """
    with open(path, 'r', encoding='utf8') as f:
        return load(f, as_class)


def write(path: str, obj, as_class: type = None):
    """
    Serialize `obj` to JSON and write it to `path`

    :param path: path to write JSON representation
    :param obj: object to serialize
    :param as_class: type or serializer
    :return: bytes written
    """
    with open(path, 'w', encoding='utf8') as f:
        return dump(f, obj, as_class)
