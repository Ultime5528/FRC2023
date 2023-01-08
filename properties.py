from networktables import NetworkTables
from networktables.util import ntproperty

persistent = True


class _Properties:
    pass
    # Exemple: aide_pilotage_slow_factor = ntproperty("/Properties/aide_pilotage_slow_factor", 0.5, writeDefault=False, persistent=persi


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
