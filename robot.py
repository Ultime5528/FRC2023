#!/usr/bin/env python3
import commands2
import wpilib

from subsystems.drivetrain import DriveTrain

from commands.drive import Drive


class Robot(commands2.TimedCommandRobot):
    def robotInit(self):
        wpilib.LiveWindow.enableAllTelemetry()
        self.drivetrain = DriveTrain()
        self.stick = wpilib.Joystick(0)
        self.drivetrain.setDefaultCommand(Drive(self.drivetrain, self.stick))


if __name__ == "__main__":
    wpilib.run(Robot)
