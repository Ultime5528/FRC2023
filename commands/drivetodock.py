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
    Climbing = "climbing"
    Stable = "stable"
    Ontop = "ontop"
    Checking = "checking"
    Balancing = "balancing"


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
    climbing_speed = autoproperty(0.18, subtable=DriveToDock.__name__)
    balancing_speed = autoproperty(0.05, subtable=DriveToDock.__name__)
    climbing_threshold = autoproperty(17.0, subtable=DriveToDock.__name__)
    ontop_threshold = autoproperty(6.0, subtable=DriveToDock.__name__)
    balancing_threshold = autoproperty(5.0, subtable=DriveToDock.__name__)
    timer_threshold = autoproperty(2.0, subtable=DriveToDock.__name__)

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
                self.state = State.Ontop

        if self.state == State.Ontop:
            speed = 0
            self.timer.start()
            if self.timer.get() > 1:
                self.state = State.Checking

        if self.state == State.Checking:
            self.timer.stop()
            self.timer.reset()
            if abs(pitch) > self.balancing_threshold:
                self.state = State.Balancing
            else:
                self.state = State.Stable

        if self.state == State.Balancing:
            if abs(pitch) > self.balancing_threshold:
                speed = math.copysign(self.balancing_speed, pitch)
            else:
                self.state = State.Ontop

        if self.state == State.Stable:
            speed = 0

        if self.backwards:
            speed *= -1

        wpilib.SmartDashboard.putString("Climbing State", self.state.value)
        self.drivetrain.arcadeDrive(speed, 0)

    def isFinished(self) -> bool:
        return self.state == State.Stable

    def end(self, interrupted: bool) -> None:
        self.drivetrain.arcadeDrive(0, 0)
