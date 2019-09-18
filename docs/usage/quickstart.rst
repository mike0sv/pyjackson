==========
Quickstart
==========

To use PyJackson in a project, define a class with type hinted constructor arguments::

    class MyPayload:
        def __init__(self, string_field: str, int_field: int):
            self.string_field = string_field
            self.int_field = int_field

..

Now you are able to serialize instance of your class to dict and back with `pyjackson.serialize` and `pyjackson.deserialize`::

    import pyjackson

    instance = MyPayload('value', 10)
    payload = pyjackson.serialize(instance)  # {'string_field': 'value', 'int_field': 10}

    new_instance = pyjackson.deserialize(payload, MyPayload)  # MyPayload('value', 10)

..

It also works with nested structures and supports `typing` module generic annotations::

    import typing

    class PayloadList:
        def __init__(self, payload_list: typing.List[MyPayload]):
            self.payload_list = payload_list

    plist = PayloadList([instance])
    payloads = pyjackson.serialize(plist)
    # {'payload_list': [{'string_field': 'value', 'int_field': 10}]}

..
