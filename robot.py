#!/usr/bin/env python3

import commands2
from networktables import NetworkTables
import wpilib
import commands
from wpimath.geometry import Pose2d
from wpilib import SmartDashboard
from subsystems.drivetrain import Drivetrain

from commands.followtrajectory import FollowTrajectory


class Robot(commands2.TimedCommandRobot):
    def robotInit(self):
        self.drivetrain = Drivetrain()
        NetworkTables.initialize("127.0.0.1")
        SmartDashboard.putData("Follow Trajectory", FollowTrajectory(self.drivetrain, [self.drivetrain.getPose(), Pose2d(0, 5, 0), Pose2d(8, 5, 90)], 0.6))

    def robotPeriodic(self) -> None:
        # Tu doit mettre ceci sinon le CommandScheduler ne marche pas pour une raison X
        commands2.CommandScheduler.getInstance().run()

    def autonomousPeriodic(self):
        pass


if __name__ == "__main__":
    wpilib.run(Robot)
