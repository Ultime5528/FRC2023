import wpilib
from commands2 import CommandBase
import properties
from subsystems.drivetrain import Drivetrain


class DriveToDock(CommandBase):
    def __init__(self, drivetrain: Drivetrain):
        super().__init__()
        self.drivetrain = drivetrain
        self.addRequirements(drivetrain)
        self.moving_average = 1

    def execute(self) -> None:
        _calculated_speed = (properties.values.drive_to_dock_speed_max * Drivetrain.getPitch() / 180)
        self.drivetrain.arcadeDrive(_calculated_speed, 0)
        self.moving_average = (self.moving_average + Drivetrain.getPitch()/180)/2

    def isFinished(self) -> bool:
        return abs(self.moving_average) < properties.values.drive_to_dock_angle_threshold

    def end(self, interrupted: bool) -> None:
        self.drivetrain.arcadeDrive(0, 0)


