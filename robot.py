#!/usr/bin/env python3
import commands2
from networktables import NetworkTables
import wpilib
import commands
from wpimath.geometry import Pose2d
from wpilib import SmartDashboard
from subsystems.drivetrain import Drivetrain

from commands.followtrajectory import FollowTrajectory

from commands.drive import Drive


class Robot(commands2.TimedCommandRobot):
    def robotInit(self):
        wpilib.LiveWindow.enableAllTelemetry()
        NetworkTables.initialize("127.0.0.1")
        self.drivetrain = Drivetrain()
        self.stick = wpilib.Joystick(0)
        self.drivetrain.setDefaultCommand(Drive(self.drivetrain, self.stick))


if __name__ == "__main__":
    wpilib.run(Robot)
