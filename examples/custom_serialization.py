from typing import List

from pyjackson import deserialize, serialize
from pyjackson.generics import Serializer, StaticSerializer


class External:
    def __init__(self, a):
        self.b = a


class ExternalSerializer(StaticSerializer):
    real_type = External

    @classmethod
    def serialize(cls, instance: External) -> dict:
        return {'a': instance.b}

    @classmethod
    def deserialize(cls, obj: dict) -> object:
        return External(obj['a'])


payload = serialize(External('value'))  # {'a': 'value'}
new_instance = deserialize(payload, External)  # External('value')


class Container:
    def __init__(self, externals: List[External]):
        self.externals = externals


container_payload = serialize(Container([External('value')]))
new_container = deserialize(container_payload, Container)


class SizedListSerializer(Serializer):
    real_type = list

    def __init__(self, size: int):
        self.size = size

    def serialize(self, instance: list) -> dict:
        if len(set(instance)) != 1:
            raise ValueError('Cannot serialize list with different values')
        return {'value': instance[0]}

    def deserialize(self, obj: dict) -> object:
        value = obj['value']
        return [value for _ in range(self.size)]


serializer = SizedListSerializer(3)

list_payload = serialize([1, 1, 1], serializer)  # {'value': 1}
new_list = deserialize(list_payload, serializer)  # [1, 1 ,1]


class OtherContainer:
    def __init__(self, sized_list: SizedListSerializer(3)):
        self.sized_list = sized_list


other_payload = serialize(OtherContainer([2, 2, 2]))  # {'sized_list': {'value': 2}}
new_other_container = deserialize(other_payload, OtherContainer)  # OtherContainer([2, 2, 2])

if __name__ == '__main__':
    print(payload, new_instance)
    print(container_payload, new_container)
    print(list_payload, new_list)
    print(other_payload, new_other_container)
