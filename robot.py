#!/usr/bin/env python3
import math

import commands2
import wpilib
from commands2 import Trigger
from commands2.button import JoystickButton
from wpimath.geometry import Pose2d

from commands.autonomous import placeandgetobject, placeandgetobjectandchargingstation
from commands.closeclaw import CloseClaw
from commands.drive import Drive
from commands.drivetodock import DriveToDock
from commands.drop import Drop
from commands.followtrajectory import FollowTrajectory
from commands.gogrid import GoGrid
from commands.manualelevate import ManualElevate
from commands.manualextend import ManualExtend
from commands.movearm import MoveArm, MoveArmDirect
from commands.openclaw import OpenClaw
from commands.resetarm import ResetArm
from commands.slowdrive import SlowDrive
from commands.takeobject import TakeObject
from commands.turn import Turn
from subsystems.arm import Arm
from subsystems.claw import Claw
from subsystems.drivetrain import Drivetrain
from utils.property import clear_autoproperties
from utils.safecommand import SafeCommand


class Robot(commands2.TimedCommandRobot):
    def robotInit(self):
        wpilib.LiveWindow.enableAllTelemetry()
        wpilib.LiveWindow.setEnabled(True)

        self.stick = wpilib.Joystick(0)
        self.panel = wpilib.Joystick(1)

        self.drivetrain = Drivetrain()
        self.arm = Arm()
        self.claw = Claw()

        self.drivetrain.setDefaultCommand(Drive(self.drivetrain, self.stick))
        #JoystickButton(self.stick, 1).whenPressed(MoveArm(self.arm, 2, 2))

        
        Trigger(self.arm.hasObject).onTrue(TakeObject(self.claw, self.arm))

        #self.setup_buttons()
        self.setup_dashboard()

        # Doit être à la fin, après que tout ait été instancié
        clear_autoproperties()

    def autonomousInit(self) -> None:
        self.autoCommand = self.autoChooser.getSelected()

        if self.autoCommand:
            self.autoCommand.schedule()

    def teleopInit(self) -> None:
        if self.autoCommand:
            self.autoCommand.cancel()

    def setup_buttons(self):
        # Pilot
        JoystickButton(self.stick, 1).whenPressed(SlowDrive(self.drivetrain, self.stick))
        JoystickButton(self.stick, 2).whenPressed(OpenClaw(self.claw))
        JoystickButton(self.stick, 3).whenPressed(CloseClaw(self.claw))

        # Copilot
        JoystickButton(self.panel, 1).whenPressed(GoGrid(self.drivetrain, "1"))
        JoystickButton(self.panel, 2).whenPressed(GoGrid(self.drivetrain, "2"))
        JoystickButton(self.panel, 3).whenPressed(GoGrid(self.drivetrain, "3"))
        JoystickButton(self.panel, 4).whenPressed(GoGrid(self.drivetrain, "4"))
        JoystickButton(self.panel, 5).whenPressed(GoGrid(self.drivetrain, "5"))
        JoystickButton(self.panel, 6).whenPressed(GoGrid(self.drivetrain, "6"))
        JoystickButton(self.panel, 7).whenPressed(GoGrid(self.drivetrain, "7"))
        JoystickButton(self.panel, 8).whenPressed(GoGrid(self.drivetrain, "8"))
        JoystickButton(self.panel, 9).whenPressed(GoGrid(self.drivetrain, "9"))
        JoystickButton(self.panel, 10).whenPressed(MoveArm.toLevel1(self.arm))
        JoystickButton(self.panel, 11).whenPressed(MoveArm.toLevel2(self.arm))
        JoystickButton(self.panel, 12).whenPressed(MoveArm.toLevel3(self.arm))
        JoystickButton(self.panel, 13).whenPressed(MoveArm.toFloor(self.arm))
        JoystickButton(self.panel, 14).whenPressed(MoveArm.toBase(self.arm))
        # JoystickButton(self.panel, 15).whenPressed(ledpourcube))
        # JoystickButton(self.panel, 16).whenPressed(ledpourcône))
        # JoystickButton(self.panel, 17).whenPressed(Drop(self.claw)

    def setup_dashboard(self):
        put_command_on_dashboard("Drivetrain", SlowDrive(self.drivetrain, self.stick))
        put_command_on_dashboard("Drivetrain", FollowTrajectory(self.drivetrain, Pose2d(1.2, -0.7, math.radians(-33)), 0.18, "relative"), "curve")
        put_command_on_dashboard("Drivetrain", FollowTrajectory.driveStraight(self.drivetrain, 2.00, 0.1))
        put_command_on_dashboard("Drivetrain", FollowTrajectory.toLoading(self.drivetrain))
        put_command_on_dashboard("Drivetrain", Turn(self.drivetrain, 45, 0.28))
        put_command_on_dashboard("Drivetrain", DriveToDock(self.drivetrain))
        put_command_on_dashboard("Drivetrain", GoGrid(self.drivetrain, "7"), name="GoGrid.7")
        put_command_on_dashboard("Drivetrain", GoGrid(self.drivetrain, "8"), name="GoGrid.8")
        put_command_on_dashboard("Drivetrain", GoGrid(self.drivetrain, "9"), name="GoGrid.9")
        put_command_on_dashboard("Claw", OpenClaw(self.claw))
        put_command_on_dashboard("Claw", CloseClaw(self.claw))
        put_command_on_dashboard("Arm", ResetArm(self.arm))
        put_command_on_dashboard("Arm", MoveArm.toLevel1(self.arm))
        put_command_on_dashboard("Arm", MoveArm.toLevel2(self.arm))
        put_command_on_dashboard("Arm", MoveArm.toLevel3(self.arm))
        put_command_on_dashboard("Arm", MoveArm.toFloor(self.arm))
        put_command_on_dashboard("Arm", MoveArm.toBase(self.arm))
        put_command_on_dashboard("Arm", MoveArm.toBin(self.arm))
        put_command_on_dashboard("Arm", MoveArmDirect.toTransition(self.arm))
        put_command_on_dashboard("ArmManual", ManualElevate.up(self.arm))
        put_command_on_dashboard("ArmManual", ManualElevate.down(self.arm))
        put_command_on_dashboard("ArmManual", ManualExtend.up(self.arm))
        put_command_on_dashboard("ArmManual", ManualExtend.down(self.arm))
        put_command_on_dashboard("Groups", Drop(self.claw, self.arm))
        put_command_on_dashboard("Groups", TakeObject(self.claw, self.arm))

        self.autoCommand: commands2.CommandBase = None
        self.autoChooser = wpilib.SendableChooser()
        self.autoChooser.setDefaultOption("Rien", None)
        self.autoChooser.addOption("Placer et prendre", placeandgetobject.PlaceAndGetObject(self.drivetrain, self.claw, self.arm))
        self.autoChooser.addOption("Placer, prendre et station de charge", placeandgetobjectandchargingstation.PlaceAndGetObjectAndChargingStation(self.drivetrain, self.claw, self.arm))

        wpilib.SmartDashboard.putData("ModeAutonome", self.autoChooser)
        # put_command_on_dashboard("Led", ledpourcube)
        # put_command_on_dashboard("Led", lespourtriangle)


def put_command_on_dashboard(sub_table: str, cmd: commands2.CommandBase, name=None):
    if sub_table:
        sub_table += "/"
    else:
        sub_table = ""

    if name is None:
        name = cmd.getName()
    else:
        cmd.setName(name)

    wpilib.SmartDashboard.putData(sub_table + name, cmd)

    return cmd


if __name__ == "__main__":
    wpilib.run(Robot)
