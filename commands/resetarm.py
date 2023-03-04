from subsystems.arm import Arm
from utils.property import autoproperty
from utils.safecommand import SafeCommand


class ResetArm(SafeCommand):
    elevator_speed = autoproperty(0.1)
    extension_speed = autoproperty(0.1)

    def __init__(self, arm: Arm):
        super().__init__()
        self.arm = arm
        self.addRequirements(self.arm)

    def execute(self) -> None:
        if not self.arm.isSwitchElevatorMinOn():
            self.arm.setElevatorSpeed(-self.elevator_speed)
        else:
            self.arm.setElevatorSpeed(0.0)

        if not self.arm.isSwitchExtensionMinOn():
            self.arm.setExtensionSpeed(-self.extension_speed)
        else:
            self.arm.setExtensionSpeed(0.0)

    def isFinished(self) -> bool:
        return self.arm.isSwitchElevatorMinOn() and self.arm.isSwitchExtensionMinOn()

    def end(self, interrupted: bool) -> None:
        self.arm.setElevatorSpeed(0.0)
        self.arm.setExtensionSpeed(0.0)
