import json
from datetime import datetime

try:
    import orjson
except ModuleNotFoundError:
    HAS_ORJSON = False
else:
    HAS_ORJSON = True

if HAS_ORJSON:
    from_json = orjson.loads
    to_dump = orjson.dumps
else:
    from_json = json.loads
    to_dump = json.dumps


class Pointer:
    def __init__(self):
        self._pointer_value = []

    def _add_pointer(self, value) -> int:
        self._pointer_value.append(value)
        return len(self._pointer_value) - 1

    def _get_pointer(self, position: int) -> str:
        return self._pointer_value.pop(position)


def dump(data):
    return to_dump(data.to_dict())


def get_datetime_to_string(time: datetime) -> str:
    now = datetime.now()
    _time = now - time
    if _time.days > 365:
        return time.strftime("%y년 %m월 %d일")
    elif _time.days > 31:
        return time.strftime("%m월 %d일")
    elif _time.days > 0:
        return time.strftime("{0}일 전".format(_time.days))
    elif _time.total_seconds() > 3600:
        second = _time.total_seconds()
        hours = int(second / 3600)
        return "{0}시간 전".format(hours)
    elif _time.total_seconds() > 60:
        second = _time.total_seconds()
        hours = int(second / 60)
        return "{0}분 전".format(hours)
    else:
        return "{0}초 전".format(_time.total_seconds())