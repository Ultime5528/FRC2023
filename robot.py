#!/usr/bin/env python3
import commands2
import numpy as np
import wpilib
from led import LEDController
from subsystems.drivetrain import Drivetrain
from commands2.button import JoystickButton
from commands.drive import Drive


class Robot(commands2.TimedCommandRobot):
    def robotInit(self):
        wpilib.LiveWindow.enableAllTelemetry()
        self.drivetrain = Drivetrain()
        self.stick = wpilib.Joystick(0)
        self.drivetrain.setDefaultCommand(Drive(self.drivetrain, self.stick))
        self.led_controller = LEDController()
        JoystickButton(self.stick,1).whenPressed(self.led_controller.rainbow())


if __name__ == "__main__":
    wpilib.run(Robot)
