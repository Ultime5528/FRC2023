#!/usr/bin/env python3

import commands2
from commands2 import Trigger
import numpy as np
import wpilib

from commands.drivetodock import DriveToDock
from commands.drop import Drop
from commands.gogrid import GoGrid
from commands.manualextend import ManualExtend
from commands.movearm import MoveArm
from commands.takeobject import TakeObject
from commands2.button import JoystickButton
from commands2.button import JoystickButton
from wpimath.geometry import Pose2d

from commands.basicfollowtrajectory import BasicFollowTrajectory
from commands.closeclaw import CloseClaw
from commands.drive import Drive
from commands.manualelevate import ManualElevate
from commands.movearm import MoveArm
from subsystems.arm import Arm
from commands.followtrajectory import FollowTrajectory
from commands.openclaw import OpenClaw
from commands.slowdrive import SlowDrive
from commands.turn import Turn
from subsystems.arm import Arm
from subsystems.claw import Claw
from subsystems.drivetrain import Drivetrain
from commands.followtrajectory import FollowTrajectory
from subsystems.arm import Arm
from commands.movearm import MoveArm
from utils.property import clear_autoproperties


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

        Trigger(self.arm.getPhotocell).onTrue(TakeObject(self.claw, self.arm))

        self.setup_buttons()
        self.setup_dashboard()

        # Doit être à la fin, après que tout ait été instancié
        clear_autoproperties()

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
        put_command_on_dashboard("Drivetrain", FollowTrajectory(self.drivetrain, Pose2d(5, 1, 0), 1, "absolute"))
        put_command_on_dashboard("Drivetrain", Turn(self.drivetrain, 180, 0.5))
        put_command_on_dashboard("Drivetrain", DriveToDock(self.drivetrain))
        put_command_on_dashboard("Claw", OpenClaw(self.claw))
        put_command_on_dashboard("Claw", CloseClaw(self.claw))
        put_command_on_dashboard("Arm", MoveArm.toLevel1(self.arm))
        put_command_on_dashboard("Arm", MoveArm.toLevel2(self.arm))
        put_command_on_dashboard("Arm", MoveArm.toLevel3(self.arm))
        put_command_on_dashboard("Arm", MoveArm.toFloor(self.arm))
        put_command_on_dashboard("Arm", MoveArm.toBase(self.arm))
        put_command_on_dashboard("Arm", MoveArm.toBin(self.arm))
        put_command_on_dashboard("Arm", MoveArm.toTransition(self.arm))
        put_command_on_dashboard("ArmManual", ManualElevate.up(self.arm))
        put_command_on_dashboard("ArmManual", ManualElevate.down(self.arm))
        put_command_on_dashboard("ArmManual", ManualExtend.up(self.arm))
        put_command_on_dashboard("ArmManual", ManualExtend.down(self.arm))
        put_command_on_dashboard("Groups", Drop(self.claw, self.arm))
        put_command_on_dashboard("Groups", TakeObject(self.claw, self.arm))

        # put_command_on_dashboard("Led", ledpourcube)
        # put_command_on_dashboard("Led", lespourtriangle)


def put_command_on_dashboard(sub_table: str, cmd: commands2.CommandBase, name=None):
    if sub_table:
        sub_table += "/"
    else:
        sub_table = ""

    if name is None:
        name = cmd.getName()

    wpilib.SmartDashboard.putData(sub_table + name, cmd)

    return cmd


if __name__ == "__main__":
    wpilib.run(Robot)
