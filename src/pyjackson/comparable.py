import inspect


class Comparable:
    def __eq__(self, other):
        cls = type(self)
        if cls != type(other):
            return False

        args = inspect.getfullargspec(cls.__init__).args[1:]
        for a in args:
            if getattr(self, a) != getattr(other, a):
                return False
        return True
