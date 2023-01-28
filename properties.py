from utils.property import autoproperty


class _CommonProperties:
    """
    Respect the naming convention : "subsystem/command" _ "variable type" _ "precision"

    Example:
        my_variable_name = autoproperty(0.5)  # Default value is 0.5
    """


common = _CommonProperties()
