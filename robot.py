#!/usr/bin/env python3
import math
import commands2
import wpilib
from wpimath.geometry import Pose2d

from commands.drive import Drive
from subsystems.drivetrain import Drivetrain
from utils.property import clear_autoproperties

from commands.drive import Drive
from commands.followtrajectory import FollowTrajectory

from utils.dashboard import putCommandOnDashboard


class Robot(commands2.TimedCommandRobot):
    def robotInit(self):
        wpilib.LiveWindow.enableAllTelemetry()
        wpilib.LiveWindow.setEnabled(True)

        self.drivetrain = Drivetrain()
        self.stick = wpilib.Joystick(0)
        self.drivetrain.setDefaultCommand(Drive(self.drivetrain, self.stick))

        self.setupDashboard()
        # Doit être à la fin, après que tout ait été instancié
        clear_autoproperties()

    def setupDashboard(self):
        putCommandOnDashboard("Déplacer", FollowTrajectory(self.drivetrain, [self.drivetrain.getPose(), Pose2d(0, 3, math.radians(90)), Pose2d(3, 3, 0)], 0.5))

if __name__ == "__main__":
    wpilib.run(Robot)
