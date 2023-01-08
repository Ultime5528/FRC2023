from networktables import NetworkTables
from networktables.util import ntproperty

persistent = True

"""
Respect the naming convention : "subsystem" _ "command" _ "precision"
Example: climber_climb-high_speed
"""


class _Properties:
    pass
    # Example: shooter_speed = ntproperty("/Properties/shooter_speed", 1500, writeDefault=False, persistent=persistent)


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
