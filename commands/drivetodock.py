import wpilib
from commands2 import CommandBase
import properties
from subsystems.drivetrain import Drivetrain

_minimal_drive_speed = 0.25
_angle_threshold = 0.5
_timer_threshold = 2

class DriveToDock(CommandBase):
    def __init__(self, drivetrain: Drivetrain):
        super().__init__()
        self.drivetrain = drivetrain
        self.addRequirements(drivetrain)
        self.has_docked = False
        self.timer = wpilib.Timer

    def initialize(self) -> None:
        self.timer.reset()

    def execute(self) -> None:
        _pitch = self.drivetrain.getPitch()
        _calculated_speed = (_pitch / abs(_pitch)) * (_minimal_drive_speed + abs(_pitch))
        self.drivetrain.arcadeDrive(_calculated_speed, 0)

        if _pitch <= _angle_threshold and self.has_docked:
            self.timer.start()
        else:
            self.timer.stop()
        if _pitch > 10:
            self.has_docked = True

    def isFinished(self) -> bool:
        return self.timer.get() < _timer_threshold

    def end(self, interrupted: bool) -> None:
        self.drivetrain.arcadeDrive(0, 0)
