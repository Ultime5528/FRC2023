#!/usr/bin/env python3

import commands2
import wpilib
from commands2.button import JoystickButton

from commands.autonomous import placeandgetobject, placeandgetobjectandchargingstation
from commands.drive import Drive
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

        self.autoCommand: commands2.CommandBase = None
        self.autoChooser = wpilib.SendableChooser()
        self.autoChooser.setDefaultOption("Rien", None)
        self.autoChooser.addOption("Placer et prendre", placeandgetobject.PlaceAndGetObject(self.drivetrain, self.claw, self.arm))
        self.autoChooser.addOption("Placer, prendre et station de charge", placeandgetobjectandchargingstation.PlaceAndGetObjectAndChargingStation(self.drivetrain, self.claw, self.arm))

        wpilib.SmartDashboard.putData("ModeAutonome", self.autoChooser)

        # Doit être à la fin, après que tout ait été instancié
        clear_autoproperties()

    def autonomousInit(self) -> None:
        self.autoCommand = self.autoChooser.getSelected()

        if self.autoCommand:
            self.autoCommand.schedule()

    def teleopInit(self) -> None:
        if self.autoCommand:
            self.autoCommand.cancel()

if __name__ == "__main__":
    wpilib.run(Robot)
