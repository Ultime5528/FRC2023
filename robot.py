#!/usr/bin/env python3
import math

import commands2
import wpilib
from wpimath.geometry import Pose2d

from subsystems.drivetrain import Drivetrain

from commands.drive import Drive
from commands2.button import JoystickButton
from commands.followtrajectory import FollowTrajectory


class Robot(commands2.TimedCommandRobot):
    def robotInit(self):
        wpilib.LiveWindow.enableAllTelemetry()
        self.drivetrain = Drivetrain()
        self.stick = wpilib.Joystick(0)
        self.drivetrain.setDefaultCommand(Drive(self.drivetrain, self.stick))
        JoystickButton(self.stick, 1).whenPressed(FollowTrajectory(self.drivetrain, [Pose2d(1, 0, 0)], 0.75, origin="Relative"))
        JoystickButton(self.stick, 2).whenPressed(FollowTrajectory(self.drivetrain, [Pose2d(1, 0, 0)], 0.75, origin="Absolute"))
        JoystickButton(self.stick, 3).whenPressed(FollowTrajectory(self.drivetrain, [Pose2d(1, 0, 0)], 0.75, origin="Absolute", direction="Backward"))
        JoystickButton(self.stick, 4).whenPressed(FollowTrajectory(self.drivetrain, [Pose2d(4, 4, math.radians(180))], 0.75, origin="Absolute", direction="Backward"))

if __name__ == "__main__":
    wpilib.run(Robot)
