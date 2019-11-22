from tests.conftest import RootClass


class ChildClass(RootClass):
    def __init__(self, field: str):
        self.field = field
