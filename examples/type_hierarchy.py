from pyjackson import deserialize, serialize
from pyjackson.decorators import type_field


@type_field('type_alias')
class Parent:
    type_alias = 'parent'  # also could be None for abstract parents


class Child1(Parent):
    type_alias = 'child1'

    def __init__(self, a: int):
        self.a = a


class Child2(Parent):
    type_alias = 'child2'

    def __init__(self, b: str):
        self.b = b


serialize(Child1(1), Parent)  # {'type_alias': 'child1', 'a': 1}
deserialize({'type_alias': 'child2', 'b': 'b'}, Parent)  # Child2('b')
