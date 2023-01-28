from typing import Optional

from ntcore import NetworkTableInstance
from ntcore.util import ntproperty as _old_ntproperty


write_default = False
default_persistent = True
registry = []


def autoproperty(
    default_value,
    key: Optional[str] = None,
    table: Optional[str] = None,
    full_key: Optional[str] = None,
    write: Optional[bool] = None
):
    assert full_key is None or (key is None and table is None)

    if full_key is None:
        import inspect
        curframe = inspect.currentframe()
        calframes = inspect.getouterframes(curframe, 1)
        calframe = calframes[1]

        if table is None:
            class_name = calframe.function
            table = "/Properties/" + class_name

        if key is None:
            code_line = calframe.code_context[0]
            key = code_line.split("=")[0].strip()

        full_key = table + "/" + key

    write = write if write is not None else write_default

    registry.append(full_key)

    return _old_ntproperty(full_key, default_value, writeDefault=write, persistent=default_persistent)


def clear_autoproperties():
    topics = NetworkTableInstance.getDefault().getTopics()
    for topic in topics:
        name = topic.getName()
        if name.startswith("/Properties/"):
            if name not in registry:
                topic.setPersistent(False)
                print("Deleted unused persistent property:", name)