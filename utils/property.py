from typing import Optional, Union, Callable

from ntcore import NetworkTableInstance
from ntcore.util import ntproperty as _old_ntproperty

write_default = False
default_persistent = True
registry = []

FloatProperty = Union[float, Callable[[], float]]


def asCallable(val: FloatProperty) -> Callable[[], float]:
    if callable(val):
        return val
    return lambda: val


def defaultSetter(value):
    pass


_DEFAULT_CLASS_NAME = object()


def autoproperty(
        default_value,
        key: Optional[str] = None,
        table: Optional[str] = None,
        subtable: Optional[str] = _DEFAULT_CLASS_NAME,
        full_key: Optional[str] = None,
        write: Optional[bool] = None
):
    assert full_key is None or (key is None and table is None and subtable is None)

    if full_key is None:
        import inspect
        curframe = inspect.currentframe()
        calframes = inspect.getouterframes(curframe, 1)
        calframe = calframes[1]

        if table is None:
            table = "Properties"

        if not table.startswith("/"):
            table = "/" + table

        if not table.endswith("/"):
            table += "/"

        if subtable is _DEFAULT_CLASS_NAME:
            subtable = calframe.function

        if subtable is not None:
            table += subtable + "/"

        if key is None:
            code_line = calframe.code_context[0]
            key = code_line.split("=")[0].strip()

        full_key = table + key

    write = write if write is not None else write_default

    registry.append(full_key)

    return _old_ntproperty(full_key, default_value, writeDefault=write, persistent=default_persistent)


def clearAutoproperties():
    topics = NetworkTableInstance.getDefault().getTopics()
    for topic in topics:
        name = topic.getName()
        if name.startswith("/Properties/"):
            if name not in registry:
                topic.setPersistent(False)
                print("Deleted unused persistent property:", name)
