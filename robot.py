#!/usr/bin/env python3

import commands2
import wpilib
from commands2.button import JoystickButton

from commands.basicfollowtrajectory import BasicFollowTrajectory
from commands.drive import Drive
from utils.property import clear_autoproperties


class Robot(commands2.TimedCommandRobot):
    def robotInit(self):
        wpilib.LiveWindow.enableAllTelemetry()
        wpilib.LiveWindow.setEnabled(True)

        self.drivetrain = Drivetrain()
        self.arm = Arm()
        self.stick = wpilib.Joystick(0)

        self.drivetrain.setDefaultCommand(Drive(self.drivetrain, self.stick))

        self.drivetrain.setDefaultCommand(Drive(self.drivetrain, self.stick))
        JoystickButton(self.stick, 1).whenPressed(MoveArm(self.arm, 2, 2))
        # Doit être à la fin, après que tout ait été instancié
        clear_autoproperties()


if __name__ == "__main__":
    wpilib.run(Robot)
