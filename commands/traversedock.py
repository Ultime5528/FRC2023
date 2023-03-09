import math

import wpilib

from subsystems.drivetrain import Drivetrain
from utils.property import autoproperty
from utils.safecommand import SafeCommand
from enum import Enum


class State(Enum):
    Start = "start"
    Up = "up"
    Down = "down"
    End = "end"


class TraverseDock(SafeCommand):
    start_speed = autoproperty(0.15)
    up_speed = autoproperty(0.1)
    down_speed = autoproperty(0.0)
    up_threshold = autoproperty(0.5)
    end_threshold = autoproperty(0.5)

    def __init__(self, drivetrain: Drivetrain):
        super().__init__()
        self.drivetrain = drivetrain
        self.addRequirements(drivetrain)
        self.state = State.Start

    def initialize(self) -> None:
        self.state = State.Start

    def execute(self) -> None:
        pitch = -self.drivetrain.getPitch()
        speed = self.start_speed

        if pitch > self.up_threshold:
            self.state = State.Up

        if self.state == State.Up:
            speed = self.up_speed
            if pitch < -self.up_threshold:
                self.state = State.Down

        if self.state == State.Down:
            speed = self.down_speed
            if abs(pitch) < self.end_threshold:
                self.state = State.End

        self.drivetrain.arcadeDrive(-speed, 0)
        print(self.state)

    def isFinished(self) -> bool:
        return self.state == State.End

    def end(self, interrupted: bool) -> None:
        self.drivetrain.arcadeDrive(0, 0)
