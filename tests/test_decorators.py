from pyjackson.decorators import cached_property, make_string, type_field


def test_make_string():
    @make_string
    class AClass:
        def __init__(self, field):
            self.field = field

    assert str(AClass('value')) == 'AClass(field=value)'


def test_cached_property__laziness():
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


def test_cached_property__instance_uniqueness():
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


def test_type_filed__metadata():
    class RootClass:
        """
        docstring
        """
        pass

    decorated = type_field('type')(RootClass)

    assert decorated.__module__ == RootClass.__module__
    assert decorated.__name__ == RootClass.__name__
    assert decorated.__doc__ == RootClass.__doc__
    assert decorated.__qualname__ == RootClass.__qualname__
