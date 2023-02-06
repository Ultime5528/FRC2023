import math

import wpilib

from subsystems.drivetrain import Drivetrain
from utils.property import autoproperty
from utils.safecommand import SafeCommand


class DriveToDock(SafeCommand):
    minimal_drive_speed = autoproperty(0.25)  # /1
    angle_threshold = autoproperty(0.5)  # degrees
    timer_threshold = autoproperty(2)  # seconds
    pitch_weight = autoproperty(0.008)  # multiplier
    pitch_threshold = autoproperty(10)

    def __init__(self, drivetrain: Drivetrain):
        super().__init__()
        self.drivetrain = drivetrain
        self.addRequirements(drivetrain)
        self.has_docked = False
        self.timer = wpilib.Timer()

    def initialize(self) -> None:
        self.has_docked = False
        self.timer.stop()
        self.timer.reset()

    def execute(self) -> None:
        _pitch = self.drivetrain.getPitch()
        _calculated_speed = math.copysign(self.minimal_drive_speed + self.pitch_weight * abs(_pitch), _pitch)
        self.drivetrain.arcadeDrive(_calculated_speed, 0)

        if _pitch > self.pitch_threshold:
            self.has_docked = True

        if _pitch <= self.angle_threshold and self.has_docked:
            self.timer.start()
        else:
            self.timer.stop()
            self.timer.reset()

    def isFinished(self) -> bool:
        return self.timer.get() > self.timer_threshold

    def end(self, interrupted: bool) -> None:
        self.drivetrain.arcadeDrive(0, 0)
