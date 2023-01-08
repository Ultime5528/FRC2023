from networktables import NetworkTables
from networktables.util import ntproperty

persistent = True

"""
Respect the naming convention : "subsystem/command" _ "variable type" _ "precision"
Example: intake_speed_slow
ntproperty strings are the same as their variables
"""


class _Properties:
    pass
# Example: intake_speed_slow = ntproperty("/Properties/intake_speed_slow", 300, writeDefault=False, persistent=persistent)


values = _Properties()


def clear_properties():
    for entry in NetworkTables.getEntries("/Properties", 0):
        name: str = entry.getName()
        assert name.startswith("/Properties/")
        name = name.replace("/Properties/", "")
        if not hasattr(values, name):
            entry.clearPersistent()
            entry.delete()
            print("Deleted", name)
