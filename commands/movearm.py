from utils.property import autoproperty
from utils.safecommand import SafeCommand
from utils.trapezoidalmotion import TrapezoidalMotion
from subsystems.arm import Arm
from subsystems.drivetrain import Drivetrain

class MoveArm(SafeCommand):

    # Elevator Properties #
    elevator_min_speed = autoproperty(0.1)
    elevator_max_speed = autoproperty(0.1)
    elevator_acceleration = autoproperty(0.001)

    # Extension Properties #
    extension_min_speed = autoproperty(0.1)
    extension_max_speed = autoproperty(0.1)
    extension_acceleration = autoproperty(0.001)

    def __init__(self, arm: Arm, drivetrain: Drivetrain, extension_end_position, elevator_end_position):
        super().__init__()

        self.drivetrain = drivetrain
        self.arm = arm
        self.extension_end_position = extension_end_position
        self.elevator_end_position = elevator_end_position

    def initialize(self) -> None:

        self.elevator_motion = TrapezoidalMotion(
           start_position=0,
           end_position=self.elevator_end_position,
           min_speed=self.elevator_min_speed,
           max_speed=self.elevator_max_speed,
           accel=self.elevator_acceleration
        )
        self.extension_motion = TrapezoidalMotion(
           start_position=0,
           end_position=self.extension_end_position,
           min_speed=self.extension_min_speed,
           max_speed=self.extension_max_speed,
           accel=self.extension_acceleration
        )

    def execute(self) -> None:
        # Elevation
        current_elevation = self.arm.getElevatorPosition()
        self.elevator_motion.setPosition(current_elevation)
        self.arm.setElevatorSpeed(self.elevator_motion.getSpeed())

        # Extension
        current_extension = self.arm.getExtensionPosition()
        self.extension_motion.setPosition(current_extension)
        self.arm.setExtensionSpeed(self.extension_motion.getSpeed())

    def isFinished(self) -> bool:
        return self.elevator_motion.isFinished() and self.extension_motion.isFinished()

    def end(self, interrupted: bool) -> None:
        pass
