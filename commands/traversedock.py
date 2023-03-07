import math

import wpilib

from subsystems.drivetrain import Drivetrain
from utils.property import autoproperty
from utils.safecommand import SafeCommand
from enum import Enum

class State(Enum):
    Start = "start"
    Climbing = "climbing"
    Stable = "end"

class TraversDock(SafeCommand):
    start_speed = autoproperty(0.15)
    climbing_speed = autoproperty(0.1)
    climbing_threshold = autoproperty(0.5)
    end_threshold = autoproperty(0.5)

    def __init__(self, drivetrain: Drivetrain):
        super().__init__()
        self.drivetrain = drivetrain
        self.addRequirements(drivetrain)
        self.state = State.Start
        self.has_docked = False

    def initialize(self) -> None:
        self.has_docked = False
        self.state = State.Start

    def execute(self) -> None:
        _pitch = -self.drivetrain.getPitch()
        speed = -self.start_speed
        if pitch > self.climbing_threshold:
            self.state = State.Climbing

        if self.state == State.Climbing:
            speed =

        self.drivetrain.arcadeDrive(speed, 0)

    def isFinished(self) -> bool:
        return abs(self.drivetrain.getPitch()) < self.angle_threshold and self.has_docked

    def end(self, interrupted: bool) -> None:
        self.drivetrain.arcadeDrive(0, 0)
