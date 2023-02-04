#!/usr/bin/env python3
import commands2
import wpilib
from commands2.button import JoystickButton
from wpimath.geometry import Pose2d

from commands.closeclaw import CloseClaw
from commands.drive import Drive
from commands.followtrajectory import FollowTrajectory
from commands.openclaw import OpenClaw
from commands.slowdrive import SlowDrive
from commands.turn import Turn
from subsystems.claw import Claw
from subsystems.drivetrain import Drivetrain
from utils.property import clear_autoproperties


def put_command_on_dashboard(sub_table: str, cmd: commands2.CommandBase, name=None):
    if sub_table:
        sub_table += "/"
    else:
        sub_table = ""

    if name is None:
        name = cmd.getName()

    wpilib.SmartDashboard.putData(sub_table + name, cmd)

    return cmd


class Robot(commands2.TimedCommandRobot):
    def robotInit(self):
        wpilib.LiveWindow.enableAllTelemetry()
        wpilib.LiveWindow.setEnabled(True)

        self.drivetrain = Drivetrain()
        self.claw = Claw()
        self.stick = wpilib.Joystick(0)
        self.drivetrain.setDefaultCommand(Drive(self.drivetrain, self.stick))

        self.setup_buttons()
        self.setup_dashboard()

        # Doit être à la fin, après que tout ait été instancié
        clear_autoproperties()

    def setup_buttons(self):
        JoystickButton(self.stick, 1).whenPressed(SlowDrive(self.drivetrain, self.stick))

    def setup_dashboard(self):
        put_command_on_dashboard("Drivetrain", SlowDrive(self.drivetrain, self.stick))
        put_command_on_dashboard("Drivetrain", FollowTrajectory(self.drivetrain, Pose2d(5, 1, 0), 1, "absolute"))
        put_command_on_dashboard("Drivetrain", Turn(self.drivetrain, 180, 0.5))
        put_command_on_dashboard("Claw", OpenClaw(self.claw))
        put_command_on_dashboard("Claw", CloseClaw(self.claw))


if __name__ == "__main__":
    wpilib.run(Robot)
