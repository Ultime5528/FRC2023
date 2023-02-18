#!/usr/bin/env python3

import commands2
import wpilib
from commands2.button import JoystickButton

from commands.basicfollowtrajectory import BasicFollowTrajectory
from commands.drive import Drive
from commands.manualelevate import ManualElevate
from commands.movearm import MoveArm
from subsystems.arm import Arm
from subsystems.drivetrain import Drivetrain
from commands.followtrajectory import FollowTrajectory
from subsystems.arm import Arm
from commands.movearm import MoveArm
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
        JoystickButton(self.stick, 2).whenPressed(ManualElevate.up(self.arm))
        JoystickButton(self.stick, 3).whenPressed(ManualElevate.down(self.arm))
        # Doit être à la fin, après que tout ait été instancié
        clear_autoproperties()


if __name__ == "__main__":
    wpilib.run(Robot)
