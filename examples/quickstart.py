import typing

import pyjackson


class MyPayload:
    def __init__(self, string_field: str, int_field: int):
        self.string_field = string_field
        self.int_field = int_field


instance = MyPayload('value', 10)
payload = pyjackson.serialize(instance)  # {'string_field': 'value', 'int_field': 10}

new_instance = pyjackson.deserialize(payload, MyPayload)  # MyPayload('value', 10)


class PayloadList:
    def __init__(self, payload_list: typing.List[MyPayload]):
        self.payload_list = payload_list


plist = PayloadList([instance])
payloads = pyjackson.serialize(plist)
# {'payload_list': [{'string_field': 'value', 'int_field': 10}]}
