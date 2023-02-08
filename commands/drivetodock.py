import wpilib
from utils.safecommand import SafeCommand
import properties
from subsystems.drivetrain import Drivetrain
from utils.property import autoproperty
import math


class DriveToDock(SafeCommand):
    minimal_drive_speed = autoproperty(0.25)
    angle_threshold = autoproperty(0.5)
    timer_threshold = autoproperty(2)
    pitch_weight = autoproperty(0.008)

    def __init__(self, drivetrain: Drivetrain):
        super().__init__()
        self.drivetrain = drivetrain
        self.addRequirements(drivetrain)
        self.has_docked = False
        self.timer = wpilib.Timer()

    def initialize(self) -> None:
        self.timer.reset()
        self.timer.stop()
        self.has_docked = False

    def execute(self) -> None:
        _pitch = self.drivetrain.getPitch()
        if _pitch <= self.angle_threshold and self.has_docked:
            self.timer.start()
            _calculated_speed = 0
        else:
            self.timer.stop()
            _calculated_speed = math.copysign((self.minimal_drive_speed + abs(_pitch)), _pitch)
        self.drivetrain.arcadeDrive(_calculated_speed, 0)
        if _pitch > 10:
            self.has_docked = True

    def isFinished(self) -> bool:
        return self.timer.get() > self.timer_threshold

    def end(self, interrupted: bool) -> None:
        self.drivetrain.arcadeDrive(0, 0)
