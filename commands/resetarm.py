from subsystems.arm import Arm
from utils.property import autoproperty
from utils.safecommand import SafeCommand


class ResetArm(SafeCommand):
    elevator_speed = autoproperty(0.25)
    extension_speed = autoproperty(0.25)

    def __init__(self, arm: Arm):
        super().__init__()
        self.arm = arm
        self.addRequirements(self.arm)

    def initialize(self) -> None:
        self.arm.is_reset = True

    def execute(self) -> None:
        if not self.arm.isSwitchElevatorMinOn():
            self.arm.setElevatorSpeed(-self.elevator_speed)
        elif not self.arm.isSwitchExtensionMinOn():
            self.arm.setElevatorSpeed(0.0)
            self.arm.setExtensionSpeed(-self.extension_speed)
        else:
            self.arm.setExtensionSpeed(0.0)

    def isFinished(self) -> bool:
        return self.arm.isSwitchElevatorMinOn() and self.arm.isSwitchExtensionMinOn()

    def end(self, interrupted: bool) -> None:
        if interrupted:
            self.arm.is_reset = False
        self.arm.setElevatorSpeed(0.0)
        self.arm.setExtensionSpeed(0.0)
