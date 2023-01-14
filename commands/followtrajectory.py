import math
from typing import List

import wpimath.trajectory
from wpimath.geometry import Pose2d, Transform2d
from wpimath.trajectory import TrajectoryConfig, TrajectoryGenerator

from properties import values

from utils.safecommandbase import SafeCommandBase
from utils.trapezoidalmotion import TrapezoidalMotion
from subsystems.drivetrain import Drivetrain


class FollowTrajectory(SafeCommandBase):
    """
    Pour une trajectoire inversée, il faut :
    - reversed=True
    - Les angles doivent être inversés (0 devient 180, -30 devient 150...)
    - Les coordonnées doivent être multipliées par -1 : (3, -1) devient (-3, 1)
    """

    def __init__(
            self,
            drivetrain: Drivetrain,
            waypoints: List[Pose2d],
            speed: float,
            reset: bool = False,
            add_robot_pose: bool = False,
            _reversed: bool = False
    ) -> None:
        super().__init__()
        self.waypoints = waypoints
        self.drivetrain = drivetrain
        self.addRequirements(drivetrain)
        self.speed = speed
        self.add_robot_pose = add_robot_pose
        self.reversed = _reversed
        self.config = TrajectoryConfig(10, 10)
        self.config.setReversed(self.reversed)

        if not self.add_robot_pose:
            self.trajectory = TrajectoryGenerator.generateTrajectory(
                self.waypoints, self.config
            )
            # transformation = wpimath.geometry._geometry.Transform2d(self.drivetrain.getPose().translation(), wpimath.geometry._geometry.Rotation2d(math.radians(self.drivetrain.getAngle())))
            # self.trajectory = self.trajectory.transformBy(transformation)

            self.states = self.trajectory.states()

    def initialize(self) -> None:
        if self.add_robot_pose:
            self.trajectory = TrajectoryGenerator.generateTrajectory(
                [self.drivetrain.getPose(), *self.waypoints],
                self.config
            )
            self.states = self.trajectory.states()

        self.motion = TrapezoidalMotion(
            start_speed=0.1,
            end_speed=self.speed,
            accel=0.08,
            start_position=0,
            displacement=self.states[0].pose.translation().distance(self.states[-1].pose.translation())
        )

        self.index = 0
        self.cumul_dist = 0
        self.start_dist = self.drivetrain.getAverageEncoderPosition()
        self.drivetrain.getField().getObject("traj").setTrajectory(self.trajectory)

    def execute(self) -> None:
        currentPose = self.drivetrain.getPose()

        while (
                self.index < len(self.states) - 1
                and abs(self.drivetrain.getAverageEncoderPosition() - self.start_dist) >= self.cumul_dist
        ):
            self.index += 1
            self.cumul_dist += self.states[self.index].pose.translation().distance(
                self.states[self.index - 1].pose.translation())

        poseDest = self.states[self.index].pose
        traversed = self.states[0].pose.translation().distance(poseDest.translation())
        self.motion.set_position(traversed)
        speed = self.motion.get_speed() * (-1 if self.reversed else 1)

        error = currentPose.rotation() - poseDest.rotation()

        correction = values.trajectory_correction_angle * error.degrees()
        self.drivetrain.tankDrive(speed + correction, speed - correction)

    def isFinished(self) -> bool:
        return self.index >= len(self.states) - 1 and abs(
            self.drivetrain.getAverageEncoderPosition() - self.start_dist) >= self.cumul_dist

    def end(self, interrupted: bool) -> None:
        self.drivetrain.tankDrive(0, 0)
