#!/usr/bin/env python3
import math
from typing import Optional

import commands2
import wpilib
from commands2 import Trigger
from commands2.button import JoystickButton
from wpimath.geometry import Pose2d

from commands.autonomous.autodock import AutoDock
from commands.autonomous.autoline import AutoLine
from commands.traversedock import TraverseDock
from commands.autonomous.autotraverse import AutoTraverse
from commands.closeclaw import CloseClaw
from commands.drive import Drive
from commands.drivestraight import DriveStraight
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
from commands.stoparm import StopArm
from commands.signalcone import SignalCone
from commands.signalcube import SignalCube
from commands.turn import Turn
from commands.autonomous.autotraversedock import AutoTraverseDock
from subsystems.arm import Arm
from subsystems.claw import Claw
from subsystems.drivetrain import Drivetrain
from subsystems.led import LEDController


class Robot(commands2.TimedCommandRobot):
    def robotInit(self):
        wpilib.LiveWindow.enableAllTelemetry()
        wpilib.LiveWindow.setEnabled(True)
        wpilib.DriverStation.silenceJoystickConnectionWarning(True)

        self.autoCommand: Optional[commands2.CommandBase] = None

        self.stick = wpilib.Joystick(0)
        self.panel = wpilib.Joystick(1)

        self.drivetrain = Drivetrain()
        self.arm = Arm()
        self.claw = Claw()
        self.led_controller = LEDController()

        self.drivetrain.setDefaultCommand(Drive(self.drivetrain, self.stick))
        self.arm.setDefaultCommand(StopArm(self.arm))

        Trigger(self.arm.hasObject).onTrue(TakeObject(self.claw, self.arm))

        self.setupButtons()
        self.setupDashboard()

    def autonomousInit(self) -> None:
        self.autoCommand: commands2.CommandBase = self.autoChooser.getSelected()

        if self.autoCommand:
            self.autoCommand.schedule()

    def teleopInit(self) -> None:
        if self.autoCommand:
            self.autoCommand.cancel()

    def setupButtons(self):
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
        JoystickButton(self.panel, 15).toggleWhenPressed(SignalCone(self.led_controller))
        JoystickButton(self.panel, 16).toggleWhenPressed(SignalCube(self.led_controller))
        # JoystickButton(self.panel, 17).whenPressed(Drop(self.claw)

    def setupDashboard(self):
        putCommandOnDashboard("Drivetrain", SlowDrive(self.drivetrain, self.stick))
        putCommandOnDashboard("Drivetrain", FollowTrajectory(self.drivetrain, Pose2d(1.2, -0.7, math.radians(-33)), 0.18, "relative"), "curve")
        putCommandOnDashboard("Drivetrain", FollowTrajectory.driveStraight(self.drivetrain, 2.00, 0.1))
        putCommandOnDashboard("Drivetrain", FollowTrajectory.toLoading(self.drivetrain))
        putCommandOnDashboard("Drivetrain", DriveStraight(self.drivetrain, -1, 0.1), "DriveStraight")
        putCommandOnDashboard("Drivetrain", Turn(self.drivetrain, 45, 0.28))
        putCommandOnDashboard("Drivetrain", DriveToDock(self.drivetrain))
        putCommandOnDashboard("Drivetrain", DriveToDock(self.drivetrain, True), "DriveToDock Backwards")
        putCommandOnDashboard("Drivetrain", TraverseDock(self.drivetrain))
        putCommandOnDashboard("Drivetrain", GoGrid(self.drivetrain, "4"), name="GoGrid.4")
        putCommandOnDashboard("Drivetrain", GoGrid(self.drivetrain, "5"), name="GoGrid.5")
        putCommandOnDashboard("Drivetrain", GoGrid(self.drivetrain, "6"), name="GoGrid.6")
        putCommandOnDashboard("Drivetrain", GoGrid(self.drivetrain, "7"), name="GoGrid.7")
        putCommandOnDashboard("Drivetrain", GoGrid(self.drivetrain, "8"), name="GoGrid.8")
        putCommandOnDashboard("Drivetrain", GoGrid(self.drivetrain, "9"), name="GoGrid.9")
        putCommandOnDashboard("Claw", OpenClaw(self.claw))
        putCommandOnDashboard("Claw", CloseClaw(self.claw))
        putCommandOnDashboard("Arm", ResetArm(self.arm))
        putCommandOnDashboard("Arm", MoveArm.toLevel1(self.arm))
        putCommandOnDashboard("Arm", MoveArm.toLevel2(self.arm))
        putCommandOnDashboard("Arm", MoveArm.toLevel3(self.arm))
        putCommandOnDashboard("Arm", MoveArm.toFloor(self.arm))
        putCommandOnDashboard("Arm", MoveArm.toBase(self.arm))
        putCommandOnDashboard("Arm", MoveArm.toBin(self.arm))
        putCommandOnDashboard("Arm", MoveArmDirect.toTransition(self.arm))
        putCommandOnDashboard("ArmManual", ManualElevate.up(self.arm))
        putCommandOnDashboard("ArmManual", ManualElevate.down(self.arm))
        putCommandOnDashboard("ArmManual", ManualExtend.up(self.arm))
        putCommandOnDashboard("ArmManual", ManualExtend.down(self.arm))
        putCommandOnDashboard("Groups", Drop(self.claw, self.arm))
        putCommandOnDashboard("Groups", TakeObject(self.claw, self.arm))
        putCommandOnDashboard("Led", SignalCone(self.led_controller))
        putCommandOnDashboard("Led", SignalCube(self.led_controller))

        self.autoCommand: commands2.CommandBase = None
        self.autoChooser = wpilib.SendableChooser()
        self.autoChooser.setDefaultOption("Nothing", None)
        self.autoChooser.addOption("AutoLine drop", AutoLine(self.drivetrain, self.claw, self.arm, True))
        self.autoChooser.addOption("AutoLine no drop", AutoLine(self.drivetrain, self.claw, self.arm, False))
        self.autoChooser.addOption("AutoTraverseDock drop", AutoTraverseDock(self.drivetrain, self.claw, self.arm, True))
        self.autoChooser.addOption("AutoTraverseDock no drop", AutoTraverseDock(self.drivetrain, self.claw, self.arm, False))
        self.autoChooser.addOption("AutoTraverse drop", AutoTraverse(self.drivetrain, self.claw, self.arm, True))
        self.autoChooser.addOption("AutoTraverse no drop", AutoTraverse(self.drivetrain, self.claw, self.arm, False))
        self.autoChooser.addOption("AutoDock drop", AutoDock(self.drivetrain, self.claw, self.arm, True))
        self.autoChooser.addOption("AutoDock no drop", AutoDock(self.drivetrain, self.claw, self.arm, False))

        wpilib.SmartDashboard.putData("ModeAutonome", self.autoChooser)

        # putCommandOnDashboard("Led", ledpourcube)
        # putCommandOnDashboard("Led", lespourtriangle)


def putCommandOnDashboard(sub_table: str, cmd: commands2.CommandBase, name: str = None) -> commands2.CommandBase:
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
