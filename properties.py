from networktables import NetworkTables
from networktables.util import ntproperty
import math

persistent = True


class _Properties:
    """
    - Respect the naming convention : "subsystem/command" _ "variable type" _ "precision"
    - ntproperty strings are the same as their variables
    """

    # Example: intake_speed_slow = ntproperty("/Properties/intake_speed_slow", 300, writeDefault=False, persistent=persistent)
    drivetrain_cam_to_robot_x= 0
    drivetrain_cam_to_robot_y= 0
    drivetrain_cam_to_robot_z= 0
    def cart2sph(x, y, z):
        XsqPlusYsq = x ** 2 + y ** 2
        r = math.sqrt(XsqPlusYsq + z ** 2)  # r
        elev = math.atan2(z, math.sqrt(XsqPlusYsq))  # theta
        az = math.atan2(y, x)  # phi
        return r, elev, az
    drivetrain_cam_to_robot_spe = cart2sph(drivetrain_cam_to_robot_x, drivetrain_cam_to_robot_y, drivetrain_cam_to_robot_z)


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
