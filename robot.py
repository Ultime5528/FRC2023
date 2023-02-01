#!/usr/bin/env python3
import commands2
import wpilib
from commands2.button import JoystickButton

from commands.drive import Drive
from subsystems.drivetrain import Drivetrain
from utils.property import clear_autoproperties


class Robot(commands2.TimedCommandRobot):
    def robotInit(self):
        wpilib.LiveWindow.enableAllTelemetry()
        wpilib.LiveWindow.setEnabled(True)

        self.drivetrain = Drivetrain()
        self.stick = wpilib.Joystick(0)
        self.drivetrain.setDefaultCommand(Drive(self.drivetrain, self.stick))

        mechanism = wpilib.Mechanism2d(2, 0.1)
        root = mechanism.getRoot("arm", 0, 0)
        segment1 = root.appendLigament("segment1", 1, 0)
        self.segment2 = segment1.appendLigament("segment2", 0.5, 90)
        wpilib.SmartDashboard.putData("Mechanism", mechanism)

        # Doit être à la fin, après que tout ait été instancié
        clear_autoproperties()

    def robotPeriodic(self) -> None:
        if self.stick.getRawButton(1) == True:
            self.segment2.setAngle(self.segment2.getAngle()+1)

        if self.stick.getRawButton(2) == True:
            self.segment2.setAngle(self.segment2.getAngle() - 1)

if __name__ == "__main__":
    wpilib.run(Robot)
