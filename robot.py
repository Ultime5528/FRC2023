#!/usr/bin/env python3

import commands2
import wpilib

from wpimath.geometry import Pose2d
from wpilib import SmartDashboard
from subsystems.drivetrain import DriveTrain

from commands.followtrajectory import FollowTrajectory


class Robot(commands2.TimedCommandRobot):
    def __init__(self):
        super().__init__()
        self.drivetrain = DriveTrain()

    def robotInit(self):
        SmartDashboard.putData("Follow Trajectory", FollowTrajectory(self.drivetrain, [Pose2d(0, 0, 0), Pose2d(5, 5, 90)], 0.6))

    def robotPeriodic(self) -> None:
        pass

    def autonomousPeriodic(self):
        pass

if __name__ == "__main__":
    wpilib.run(Robot)
