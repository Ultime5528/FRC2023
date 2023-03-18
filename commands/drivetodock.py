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
    climbing_speed = autoproperty(0.3, subtable=DriveToDock.__name__)
    balancing_speed = autoproperty(0.1, subtable=DriveToDock.__name__)
    jumping_angle = autoproperty(15.0, subtable=DriveToDock.__name__)
    climbing_angle = autoproperty(10.0, subtable=DriveToDock.__name__)
    climbing_threshold = autoproperty(1.0, subtable=DriveToDock.__name__)
    ontop_threshold = autoproperty(5.0, subtable=DriveToDock.__name__)
    balancing_threshold = autoproperty(5.0, subtable=DriveToDock.__name__)
    timer_threshold = autoproperty(4.0, subtable=DriveToDock.__name__)
    jumping_time = autoproperty(0.5, subtable=DriveToDock.__name__)
    jumping_speed = autoproperty(0.2, subtable=DriveToDock.__name__)

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
            if pitch > self.jumping_angle:
                self.state = State.Jumping

        if self.state == State.Jumping:
            speed = self.jumping_speed
            self.timer.start()
            if self.timer.get() > self.jumping_time:
                self.timer.reset()
                self.state = State.Climbing

        if self.state == State.Climbing:
            self.timer.start()
            move_time = 0.3
            wait = 1
            time = self.timer.get() % (move_time + wait)
            climbing_speed = min(self.climbing_speed, max(self.climbing_speed * (abs(pitch) / self.climbing_angle), 0.1))
            if time < move_time:
                speed = math.copysign(climbing_speed, pitch)
            else:
                speed = math.copysign(0.05, pitch)

                if abs(pitch) < self.ontop_threshold and time > 1.2:
                    self.state = State.Stable

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
