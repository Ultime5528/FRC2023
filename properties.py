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

    # Example: intake_speed_slow = ntproperty("/Properties/intake_speed_slow", 300, writeDefault=False, persistent=persistent)
    drivetrain_cam_to_robot = Transform3d(Translation3d(0, 0, 0), Rotation3d(0, 0, 0))


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
