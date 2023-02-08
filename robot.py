#!/usr/bin/env python3
import math
import commands2
import wpilib
from wpimath.geometry import Pose2d
from commands2.button import JoystickButton

from commands.drive import Drive
from commands.gogrid import GoGrid
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
        JoystickButton(self.stick, 1).whenPressed(GoGrid(self.drivetrain, "3"))

        # JoystickButton(self.stick, 1).whenPressed(SlowDrive(self.drivetrain, self.stick))

        # Doit être à la fin, après que tout ait été instancié
        clear_autoproperties()

if __name__ == "__main__":
    wpilib.run(Robot)
