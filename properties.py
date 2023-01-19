from networktables import NetworkTables
from networktables.util import ntproperty

persistent = True


class _Properties:
    """
    - Respect the naming convention : "subsystem/command" _ "variable type" _ "precision"
    - ntproperty strings are the same as their variables
    """

    drive_smoothing_window = ntproperty("/Properties/drive_smoothing_window", 1, writeDefault=False, persistent=persistent)
    drive_interpolation_curve = ntproperty("/Properties/drive_interpolation_curve", 0.6, writeDefault=False, persistent=persistent)
    drive_deadzone_x = ntproperty("/Properties/drive_deadzone_x", 0.05, writeDefault=False, persistent=persistent)
    drive_deadzone_y = ntproperty("/Properties/drive_deadzone_y", 0.05, writeDefault=False, persistent=persistent)

    drive_to_dock_speed_max = ntproperty("/Propreties/drive_to_dock_speed_max", 0.5, writeDefault=False, persistent=persistent)
    drive_to_dock_angle_threshold = ntproperty("/Propreties/drive_to_dock_angle_threshold", 0.05, writeDefault=False, persistent=persistent)

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
