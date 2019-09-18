from pyjackson.decorators import cached_property, make_string


def test_make_string():
    @make_string
    class AClass:
        def __init__(self, field):
            self.field = field

    assert str(AClass('value')) == 'AClass(field=value)'


def test_cached_property_laziness():
    executed = [0]

    class WithCachedProperty:
        @cached_property
        def prop(self):
            executed[0] = executed[0] + 1
            return 'lol'

    assert executed[0] == 0

    wc1 = WithCachedProperty()

    assert executed[0] == 0

    id(wc1.prop)
    assert executed[0] == 1

    id(wc1.prop)
    assert executed[0] == 1


def test_cached_property_instance_uniqueness():
    executed = [0]

    class WithCachedProperty:
        @cached_property
        def prop(self):
            executed[0] = executed[0] + 1
            return 'lol'

    id(WithCachedProperty().prop)
    assert executed[0] == 1

    id(WithCachedProperty().prop)
    assert executed[0] == 2
