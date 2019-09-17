import json
from typing import Type, TypeVar

from .deserialization import deserialize
from .serialization import serialize


def loads(payload: str, as_class: type):
    obj = json.loads(payload)
    return deserialize(obj, as_class)


def load(fp, as_class: type):
    return loads(fp.read(), as_class)


def dumps(obj):
    payload = serialize(obj)
    return json.dumps(payload)


def dump(fp, obj):
    return fp.write(dumps(obj))


T = TypeVar('T')


def read(path: str, as_class: Type[T]) -> T:
    with open(path, 'r', encoding='utf8') as f:
        return load(f, as_class)


def write(path: str, obj):
    with open(path, 'w', encoding='utf8') as f:
        return dump(f, obj)
