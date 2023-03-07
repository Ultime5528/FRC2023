import math

import wpilib

from subsystems.drivetrain import Drivetrain
from utils.property import autoproperty
from utils.safecommand import SafeCommand
from enum import Enum

class State(Enum):
    Start = "start"
    Climbing = "climbing"
    Stable = "stable"
    Balancing = "balancing"

class DriveToDock(SafeCommand):
    start_speed = autoproperty(0.15)
    climbing_speed = autoproperty(0.1)
    balancing_speed = autoproperty(0.0)
    climbing_threshold = autoproperty(0.5)
    ontop_threshold = autoproperty(0.5)
    balancing_threshold = autoproperty(0.5)
    timer_threshold = autoproperty(2.0)

    def __init__(self, drivetrain: Drivetrain, backwards: bool = False):
        super().__init__()
        self.drivetrain = drivetrain
        self.addRequirements(drivetrain)
        self.state = State.Start
        self.timer = wpilib.Timer()
        self.max_pitch = 0
        self.backwards = backwards

    def initialize(self) -> None:
        self.state = State.Start
        self.timer.stop()
        self.timer.reset()
        self.max_pitch = 0

    def execute(self) -> None:
        pitch = self.drivetrain.getPitch()
        if self.backwards:
            pitch *= -1
        speed = 0

        if self.state == State.Start:
            speed = self.start_speed
            if pitch > self.climbing_threshold:
                self.state = State.Climbing

        if self.state == State.Climbing:
            self.max_pitch = max(self.max_pitch, pitch)
            pitch_difference = self.max_pitch - pitch
            speed = self.climbing_speed
            if pitch_difference > self.ontop_threshold:
                self.state = State.Stable

        if self.state == State.Stable:
            speed = 0
            self.timer.start()
        if self.backwards:
            speed *= -1
        self.drivetrain.arcadeDrive(speed, 0)

    def isFinished(self) -> bool:
        return self.state == State.Stable

    def end(self, interrupted: bool) -> None:
        self.drivetrain.arcadeDrive(0, 0)
