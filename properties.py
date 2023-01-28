from networktables import NetworkTables
from networktables.util import ntproperty
import math
from wpimath.geometry import Transform3d, Translation3d, Pose2d, Rotation3d

persistent = True


class _Properties:
    """
    - Respect the naming convention : "subsystem/command" _ "variable type" _ "precision"
    - ntproperty strings are the same as their variables
    """
    follow_trajectory_correction_factor = ntproperty("/Properties/follow_trajectory_correction_factor", 0.016, writeDefault=False, persistent=persistent)
    follow_trajectory_speed_start = ntproperty("/Properties/follow_trajectory_speed_start", 0.1, writeDefault=False, persistent=persistent)
    follow_trajectory_acceleration = ntproperty("/Properties/follow_trajectory_acceleration", 0.08, writeDefault=False, persistent=persistent)
    
    drive_smoothing_window = ntproperty("/Properties/drive_smoothing_window", 1, writeDefault=False, persistent=persistent)
    drive_interpolation_curve = ntproperty("/Properties/drive_interpolation_curve", 0.6, writeDefault=False, persistent=persistent)
    drive_deadzone_x = ntproperty("/Properties/drive_deadzone_x", 0.05, writeDefault=False, persistent=persistent)
    drive_deadzone_y = ntproperty("/Properties/drive_deadzone_y", 0.05, writeDefault=False, persistent=persistent)

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
