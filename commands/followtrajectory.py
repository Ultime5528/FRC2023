import math
from typing import List

import wpimath.trajectory
from wpimath.geometry import Pose2d, Transform2d, Rotation2d
from wpimath.trajectory import TrajectoryConfig, TrajectoryGenerator
from properties import values

from utils.safecommandbase import SafeCommandBase
from utils.trapezoidalmotion import TrapezoidalMotion
from subsystems.drivetrain import Drivetrain


class FollowTrajectory(SafeCommandBase):
    """
    Pour une trajectoire inversée, il faut :
    - path_reversed=True
    - Les angles doivent être inversés (0 devient 180, -30 devient 150...)
    - Les coordonnées doivent être multipliées par -1 : (3, -1) devient (-3, 1)

    Example of a command:
    FollowTrajectory(self.drivetrain, [self.drivetrain.get_pose(), Pose2d(0, 3, 90), Pose2d(3, 3, 0)], 0.5)
    """

    def __init__(
            self,
            drivetrain: Drivetrain,
            waypoints: List[Pose2d],
            speed: float,
            reset: bool = False,
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

        # Experimental but maybe what we want for reversal.
        # if self.path_reversed:
        #     for waypoint in waypoints:
        #         waypoint = Pose2d(waypoint.X() * -1, waypoint.Y() * -1, waypoint.rotation().rotateBy(Rotation2d(math.radians(180))))

        if not self.add_robot_pose:
            self.trajectory = TrajectoryGenerator.generateTrajectory(
                self.waypoints, self.config
            )

            self.states = self.trajectory.states()

    def initialize(self) -> None:
        if self.add_robot_pose:
            self.trajectory = TrajectoryGenerator.generateTrajectory(
                [self.drivetrain.get_pose(), *self.waypoints],
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
        self.start_dist = self.drivetrain.get_average_encoder_position()
        self.drivetrain.get_field().getObject("traj").setTrajectory(self.trajectory.transformBy(Transform2d(self.drivetrain.get_pose().translation(), Rotation2d(math.radians(self.drivetrain.get_angle())))))

    def execute(self) -> None:
        currentPose = self.drivetrain.get_pose()

        while (
                self.index < len(self.states) - 1
                and abs(self.drivetrain.get_average_encoder_position() - self.start_dist) >= self.cumul_dist
        ):
            self.index += 1
            self.cumul_dist += self.states[self.index].pose.translation().distance(
                self.states[self.index - 1].pose.translation())

        poseDest = self.states[self.index].pose
        traversed = self.states[0].pose.translation().distance(poseDest.translation())
        self.motion.set_position(traversed)
        speed = self.motion.get_speed() * (-1 if self.path_reversed else 1)

        error = currentPose.rotation() - poseDest.rotation()

        correction = values.trajectory_correction_angle * error.degrees()
        self.drivetrain.tank_drive(speed + correction, speed - correction)

    def isFinished(self) -> bool:
        return self.index >= len(self.states) - 1 and abs(
            self.drivetrain.get_average_encoder_position() - self.start_dist) >= self.cumul_dist

    def end(self, interrupted: bool) -> None:
        self.drivetrain.tank_drive(0, 0)
