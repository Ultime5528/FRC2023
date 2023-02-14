from ntcore import NetworkTable
from ntcore.util import ntproperty
persistent = True
from utils.property import autoproperty


class _CommonProperties:
    """
    Respect the naming convention : "subsystem/command" _ "variable type" _ "precision"

    Example:
        my_variable_name = autoproperty(0.5)  # Default value is 0.5
    """


common = _CommonProperties()


def clear_properties():
    for entry in NetworkTable.getEntry("/Properties/"):
        name: str = entry.getName()
        assert name.startswith("/Properties/")
        name = name.replace("/Properties/", "")
        if not hasattr(values, name):
            entry.clearPersistent()
            entry.delete()
            print("Deleted", name)
