#!/usr/bin/env python3
import commands2
import wpilib
from commands2._impl.button import JoystickButton

from commands.turn import Turn
from subsystems.drivetrain import Drivetrain

from commands.drive import Drive


class Robot(commands2.TimedCommandRobot):
    def robotInit(self):
        wpilib.LiveWindow.enableAllTelemetry()
        wpilib.LiveWindow.setEnabled(True)

        self.drivetrain = Drivetrain()
        self.stick = wpilib.Joystick(0)
        self.drivetrain.setDefaultCommand(Drive(self.drivetrain, self.stick))


if __name__ == "__main__":
    wpilib.run(Robot)
