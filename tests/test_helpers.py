import io

from pyjackson.core import Comparable
from pyjackson.helpers import dump, dumps, load, loads, read, write


class Payload(Comparable):
    def __init__(self, field: str):
        self.field = field


STR_PAYLOAD = '{"field": "value"}'
DICT_PAYLOAD = {'field': 'value'}
OBJ_PAYLOAD = Payload('value')


def test_read(tmp_file):
    with open(tmp_file, 'w') as f:
        f.write(STR_PAYLOAD)

    assert OBJ_PAYLOAD == read(tmp_file, Payload)


def test_write(tmp_file):
    write(tmp_file, OBJ_PAYLOAD)
    with open(tmp_file, 'r') as f:
        assert f.read() == STR_PAYLOAD


def test_loads():
    assert OBJ_PAYLOAD == loads(STR_PAYLOAD, Payload)


def test_load():
    buffer = io.StringIO(STR_PAYLOAD)
    assert OBJ_PAYLOAD == load(buffer, Payload)


def test_dumps():
    assert STR_PAYLOAD == dumps(OBJ_PAYLOAD)


def test_dump():
    buffer = io.StringIO()
    dump(buffer, OBJ_PAYLOAD)
    assert STR_PAYLOAD == buffer.getvalue()
