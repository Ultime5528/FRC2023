#!/usr/bin/env python3
import commands2
import wpilib
import wpimath.trajectory
from commands2._impl.button import JoystickButton
from wpimath._controls._controls.trajectory import TrajectoryConfig
from wpimath.geometry import Pose2d

import utils.controller
from commands.drive import Drive
from commands.slowdrive import SlowDrive
from subsystems.drivetrain import Drivetrain
from utils.property import clear_autoproperties


class Robot(commands2.TimedCommandRobot):
    def robotInit(self):
        wpilib.LiveWindow.enableAllTelemetry()
        wpilib.LiveWindow.setEnabled(True)

        self.drivetrain = Drivetrain()
        self.stick = wpilib.Joystick(0)
        self.drivetrain.setDefaultCommand(Drive(self.drivetrain, self.stick))

        JoystickButton(self.stick, 1).whenPressed(SlowDrive(self.drivetrain, self.stick))

        config = TrajectoryConfig(10, 10)
        self.traj = wpimath.trajectory.TrajectoryGenerator.generateTrajectory([Pose2d(0, 0, 0), Pose2d(5, 5, 1.57)], config)
        self.drivetrain.getField().getObject("Traj2").setTrajectory(self.traj)
        self.controller = utils.controller.RearWheelFeedbackController(self.traj)

        # Doit être à la fin, après que tout ait été instancié
        clear_autoproperties()

    def teleopPeriodic(self):
        self.controller.update(self.drivetrain.getPose())
        self.drivetrain.getField().getObject("Closest").setPose(self.controller.states[self.controller.current_idx].pose)


if __name__ == "__main__":
    wpilib.run(Robot)
