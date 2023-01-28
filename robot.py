#!/usr/bin/env python3
import commands2
import wpilib
from commands2.button import JoystickButton
from wpimath.geometry import Pose2d

from commands.followtrajectory import FollowTrajectory
from subsystems.drivetrain import Drivetrain

from commands.drive import Drive
from utils.property import clear_autoproperties


class Robot(commands2.TimedCommandRobot):
    def robotInit(self):
        wpilib.LiveWindow.enableAllTelemetry()
        wpilib.LiveWindow.setEnabled(True)

        self.drivetrain = Drivetrain()
        self.stick = wpilib.Joystick(0)
        self.drivetrain.setDefaultCommand(Drive(self.drivetrain, self.stick))
        wpilib.SmartDashboard.putData("FollowTraj", FollowTrajectory(self.drivetrain, [Pose2d(0, 0, 0)], 0.6, True))

        # Doit être à la fin, après que tout ait été instancié
        clear_autoproperties()


if __name__ == "__main__":
    wpilib.run(Robot)
