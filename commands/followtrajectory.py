import math
from typing import List

import wpimath.trajectory
from wpimath.geometry import Pose2d, Transform2d, Rotation2d
from wpimath.trajectory import TrajectoryConfig, TrajectoryGenerator

import properties

from utils.safecommand import SafeCommand
from utils.trapezoidalmotion import TrapezoidalMotion
from subsystems.drivetrain import Drivetrain


class FollowTrajectory(SafeCommand):
    """
    Pour une trajectoire inversée, il faut :
    - path_reversed=True
    - Les angles doivent être inversés (0 devient 180, -30 devient 150...)
    - Les coordonnées doivent être multipliées par -1 : (3, -1) devient (-3, 1)

    Example of a command:
    FollowTrajectory(self.drivetrain, [self.drivetrain.getPose(), Pose2d(0, 3, 90), Pose2d(3, 3, 0)], 0.5)
    """

    def __init__(
            self,
            drivetrain: Drivetrain,
            waypoints: List[Pose2d],
            speed: float,
            add_robot_pose: bool = False,
            path_reversed: bool = False
    ) -> None:
        super().__init__()
        self.waypoints = waypoints
        self.drivetrain = drivetrain
        self.addRequirements(drivetrain)
        self.speed = speed
        self.add_robot_pose = add_robot_pose
        self.path_reversed = path_reversed
        self.config = TrajectoryConfig(10, 10)
        self.config.setReversed(self.path_reversed)

        if not self.add_robot_pose:
            self.trajectory = TrajectoryGenerator.generateTrajectory(
                self.waypoints, self.config
            )

            self.states = self.trajectory.states()

    def initialize(self) -> None:
        if self.add_robot_pose:
            self.trajectory = TrajectoryGenerator.generateTrajectory(
                [self.drivetrain.getPose(), *self.waypoints],
                self.config
            )
            self.states = self.trajectory.states()

        self.motion = TrapezoidalMotion(
            min_speed=properties.values.follow_trajectory_speed_start,
            max_speed=self.speed,
            accel=properties.values.follow_trajectory_acceleration,
            start_position=0,
            displacement=self.states[0].pose.translation().distance(self.states[-1].pose.translation())
        )

        self.index = 0
        self.cumulative_dist = 0
        self.start_dist = self.drivetrain.getAverageEncoderPosition()
        self.drivetrain.getField().getObject("traj").setTrajectory(self.trajectory.transformBy(Transform2d(self.drivetrain.getPose().translation(), Rotation2d().fromDegrees(self.drivetrain.getAngle()))))

    def execute(self) -> None:
        current_pose = self.drivetrain.getPose()

        while (
                self.index < len(self.states) - 1
                and abs(self.drivetrain.getAverageEncoderPosition() - self.start_dist) >= self.cumulative_dist
        ):
            self.index += 1
            self.cumulative_dist += self.states[self.index].pose.translation().distance(
                self.states[self.index - 1].pose.translation())

        destination_pose = self.states[self.index].pose
        distance_traveled = self.states[0].pose.translation().distance(destination_pose.translation())
        self.motion.setPosition(distance_traveled)
        speed = self.motion.getSpeed() * (-1 if self.path_reversed else 1)

        error = current_pose.rotation() - destination_pose.rotation()

        correction = properties.values.follow_trajectory_correction_factor * error.degrees()
        self.drivetrain.tankDrive(speed + correction, speed - correction)

    def isFinished(self) -> bool:
        return self.index >= len(self.states) - 1 and abs(
            self.drivetrain.getAverageEncoderPosition() - self.start_dist) >= self.cumulative_dist

    def end(self, interrupted: bool) -> None:
        self.drivetrain.tankDrive(0, 0)
