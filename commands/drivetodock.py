import math

import commands2
import wpilib
from wpimath.geometry import Pose2d

from commands.followtrajectory import FollowTrajectory
from subsystems.drivetrain import Drivetrain
from utils.property import autoproperty
from utils.safecommand import SafeCommand, SafeMixin
from enum import Enum

class State(Enum):
    Start = "start"
    Jumping = "jumping"
    Climbing = "climbing"


class DriveToDock(SafeMixin, commands2.SequentialCommandGroup):
    def __init__(self, drivetrain: Drivetrain, backwards: bool = False):
        if backwards:
            drive_cmd = FollowTrajectory.driveStraight(drivetrain, 0.2, 0.1)
        else:
            drive_cmd = FollowTrajectory(drivetrain, Pose2d(-0.2, 0, math.radians(180)), -0.1, "relative", "backward")

        super().__init__(
            _DriveToDock(drivetrain, backwards)
            # drive_cmd
        )


class _DriveToDock(SafeCommand):
    start_speed = autoproperty(0.35, subtable=DriveToDock.__name__)
    climbing_factor = autoproperty(0.1, subtable=DriveToDock.__name__)
    climbing_speed = autoproperty(0.17, subtable=DriveToDock.__name__)
    jumping_angle = autoproperty(15.0, subtable=DriveToDock.__name__)
    balancing_threshold = autoproperty(5.0, subtable=DriveToDock.__name__)
    jumping_time = autoproperty(1.6, subtable=DriveToDock.__name__)
    jumping_speed = autoproperty(0.15, subtable=DriveToDock.__name__)
    derivative_threshold = autoproperty(8.5, subtable=DriveToDock.__name__)

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
        self.time = 0
        self.pitch = 0

    def execute(self) -> None:
        last_pitch = self.pitch
        last_time = self.time
        self.pitch = self.drivetrain.getPitch()
        self.time = wpilib.getTime()
        d = (self.pitch - last_pitch) / (self.time - last_time)

        if self.backwards:
            self.pitch *= -1
        speed = 0

        if self.state == State.Start:
            speed = self.start_speed
            if self.pitch > self.jumping_angle:
                self.state = State.Jumping

        if self.state == State.Jumping:
            speed = self.jumping_speed
            self.timer.start()
            if self.timer.get() > self.jumping_time:
                self.timer.reset()
                self.timer.stop()
                self.state = State.Climbing

        if self.state == State.Climbing:
            speed = self.climbing_factor * self.pitch
            speed = min(abs(speed), self.climbing_speed)
            speed = math.copysign(speed, self.pitch)
            if abs(d) > self.derivative_threshold or abs(self.pitch) < self.balancing_threshold:
                speed = 0.0

        if self.backwards:
            speed *= -1

        wpilib.SmartDashboard.putString("Climbing State", self.state.value)
        self.drivetrain.arcadeDrive(speed, 0)

    def end(self, interrupted: bool) -> None:
        self.drivetrain.arcadeDrive(0, 0)
