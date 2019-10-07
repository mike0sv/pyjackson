import typing


def is_collection36(as_class):
    return issubclass(as_class, typing.Collection) and not issubclass(as_class, typing.Dict)


def is_union36(cls):
    return isinstance(cls, typing._Union)
