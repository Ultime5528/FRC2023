from ntcore import NetworkTableInstance
from ntcore.util import ntproperty

persistent = True


class _Properties:
    """
    - Respect the naming convention : "subsystem/command" _ "variable type" _ "precision"
    - ntproperty strings are the same as their variables
    """


values = _Properties()


def check_property_names():
    import inspect
    import re

    lines = inspect.getsource(_Properties).splitlines()
    pattern = re.compile(r'^\s{4}(\w+) = ntproperty\("\/Properties\/(\w+)", [^,]+, writeDefault=False, persistent=persistent\)')

    for line in lines[1:]:
        if " = ntproperty(" in line:
            match = pattern.match(line)
            assert match, "The following property does not respect team conventions : " + line
            assert match.group(1) == match.group(2), f"Key and name of following property are not equal : {match.group(1)} != {match.group(2)}"
