import commands2
from commands2 import ConditionalCommand

from utils.property import autoproperty
from utils.safecommand import SafeCommand, SafeMixin
from utils.trapezoidalmotion import TrapezoidalMotion
from subsystems.arm import Arm


class MoveArm(SafeMixin, ConditionalCommand):
    @classmethod
    def toLevel1(cls, arm: Arm):
        cmd = cls(arm, lambda: properties.level1_extension, lambda: properties.level1_elevation)
        cmd.setName(cmd.getName() + ".toLevel1")
        return cmd

    @classmethod
    def toLevel2(cls, arm: Arm):
        cmd = cls(arm, lambda: properties.level2_extension, lambda: properties.level2_elevation)
        cmd.setName(cmd.getName() + ".toLevel2")
        return cmd

    @classmethod
    def toLevel3(cls, arm: Arm):
        cmd = cls(arm, lambda: properties.level3_extension, lambda: properties.level3_elevation)
        cmd.setName(cmd.getName() + ".toLevel3")
        return cmd

    @classmethod
    def toFloor(cls, arm: Arm):
        cmd = cls(arm, lambda: properties.floor_extension, lambda: properties.floor_elevation)
        cmd.setName(cmd.getName() + ".toFloor")
        return cmd

    @classmethod
    def toBase(cls, arm: Arm):
        cmd = cls(arm, lambda: properties.base_extension, lambda: properties.base_elevation)
        cmd.setName(cmd.getName() + ".toBase")
        return cmd

    @classmethod
    def toBin(cls, arm: Arm):
        cmd = cls(arm, lambda: properties.bin_extension, lambda: properties.bin_elevation)
        cmd.setName(cmd.getName() + ".toBin")
        return cmd

    @classmethod
    def toTransition(cls, arm: Arm):
        cmd = cls(arm, lambda: properties.transition_extension, lambda: properties.transition_elevation)
        cmd.setName(cmd.getName() + ".toTransition")
        return cmd

    def __init__(self, arm: Arm, extension_end_position, elevator_end_position):
        def cond():
            return arm.shouldTransition(extension_end_position, elevator_end_position)

        super().__init__(
            commands2.SequentialCommandGroup(
                MoveArmDirect.toTransition(arm),
                MoveArmDirect(arm, extension_end_position, elevator_end_position)
            ),
            MoveArmDirect(arm, extension_end_position, elevator_end_position),
            cond
        )


class MoveArmDirect(SafeCommand):
    # Elevator Properties #
    elevator_min_speed = autoproperty(0.1)
    elevator_max_speed = autoproperty(0.1)
    elevator_acceleration = autoproperty(0.001)

    # Extension Properties #
    extension_min_speed = autoproperty(0.1)
    extension_max_speed = autoproperty(0.1)
    extension_acceleration = autoproperty(0.001)

    @classmethod
    def toTransition(cls, arm: Arm):
        cmd = cls(arm, lambda: properties.transition_extension, lambda: properties.transition_elevation)
        cmd.setName(cmd.getName() + ".toTransition")
        return cmd

    def __init__(self, arm: Arm, extension_end_position, elevator_end_position):
        super().__init__()
        self.arm = arm
        self.extension_end_position = extension_end_position
        self.elevator_end_position = elevator_end_position

    def initialize(self) -> None:
        self.elevator_motion = TrapezoidalMotion(
            start_position=self.arm.getElevatorPosition(),
            end_position=self.elevator_end_position,
            min_speed=self.elevator_min_speed,
            max_speed=self.elevator_max_speed,
            accel=self.elevator_acceleration
        )
        self.extension_motion = TrapezoidalMotion(
            start_position=self.arm.getExtensionPosition(),
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
        self.arm.setExtensionSpeed(0)
        self.arm.setElevatorSpeed(0)


class _ClassProperties:
    level1_extension = autoproperty(0, subtable=MoveArm.__name__)
    level2_extension = autoproperty(0, subtable=MoveArm.__name__)
    level3_extension = autoproperty(0, subtable=MoveArm.__name__)
    floor_extension = autoproperty(0, subtable=MoveArm.__name__)
    base_extension = autoproperty(0, subtable=MoveArm.__name__)
    bin_extension = autoproperty(0, subtable=MoveArm.__name__)
    transition_extension = autoproperty(0, subtable=MoveArm.__name__)

    level1_elevation = autoproperty(0, subtable=MoveArm.__name__)
    level2_elevation = autoproperty(0, subtable=MoveArm.__name__)
    level3_elevation = autoproperty(0, subtable=MoveArm.__name__)
    floor_elevation = autoproperty(0, subtable=MoveArm.__name__)
    base_elevation = autoproperty(0, subtable=MoveArm.__name__)
    bin_elevation = autoproperty(0, subtable=MoveArm.__name__)
    transition_elevation = autoproperty(0, subtable=MoveArm.__name__)


properties = _ClassProperties()
