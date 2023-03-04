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
        self._has_reset_extension = False
        self._has_reset_elevator = False

    def initialize(self) -> None:
        self._has_reset_extension = False
        self._has_reset_elevator = False
        self.arm._elevator_offset = float("-inf")
        self.arm._extension_offset = float("-inf")

    def execute(self) -> None:
        if not self._has_reset_elevator:
            if self.arm._elevator_offset > float("-inf"):
                self._has_reset_elevator = True
                self.arm.motor_elevator.set(0.0)
            elif self.arm.isSwitchElevatorMinOn():
                self.arm.motor_elevator.set(self.elevator_speed)
            else:
                self.arm.motor_elevator.set(-self.elevator_speed)
        else:
            self.arm.motor_elevator.set(0.0)

        if not self._has_reset_extension:
            if self.arm._extension_offset > float("-inf"):
                self._has_reset_extension = True
                self.arm.motor_extension.set(0.0)
            elif self.arm.isSwitchExtensionMinOn():
                self.arm.motor_extension.set(self.extension_speed)
            else:
                self.arm.motor_extension.set(-self.extension_speed)
        else:
            self.arm.motor_extension.set(0.0)

    def isFinished(self) -> bool:
        return self._has_reset_extension and self._has_reset_elevator

    def end(self, interrupted: bool) -> None:
        self.arm.setElevatorSpeed(0.0)
        self.arm.setExtensionSpeed(0.0)
