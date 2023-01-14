from networktables import NetworkTables
from networktables.util import ntproperty

persistent = True


class _Properties:
    """
    - Respect the naming convention : "subsystem/command" _ "variable type" _ "precision"
    - ntproperty strings are the same as their variables
    """
    trajectory_correction_angle = ntproperty("/Properties/trajectory_correction_angle", 0.016, writeDefault=False, persistent=persistent)


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
