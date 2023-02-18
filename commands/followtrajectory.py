from typing import Literal, Iterable, Union

import wpiutil
from commands2 import ConditionalCommand
from wpilib import DriverStation
from wpimath.geometry import Pose2d, Transform2d, Translation2d, Rotation2d
from wpimath.trajectory import TrajectoryConfig, TrajectoryGenerator

from subsystems.drivetrain import Drivetrain, april_tag_field
from utils.controller import RearWheelFeedbackController
from utils.property import autoproperty, FloatProperty, as_callable, default_setter
from utils.safecommand import SafeCommand
from utils.trapezoidalmotion import TrapezoidalMotion


blue_offset = Transform2d(Translation2d(-2, 0), Rotation2d(0))
blue_loading_pose = april_tag_field.getTagPose(4).toPose2d().transformBy(blue_offset)
red_offset = Transform2d(Translation2d(2, 0), Rotation2d.fromDegrees(180))
red_loading_pose = april_tag_field.getTagPose(5).toPose2d().transformBy(red_offset)


class FollowTrajectory(SafeCommand):
    """
    Pour une trajectoire inversée, il faut :
    - path_reversed=True
    - Les angles doivent être inversés (0 devient 180, -30 devient 150...)
    - Les coordonnées doivent être multipliées par -1 : (3, -1) devient (-3, 1)

    Example of a command:
    FollowTrajectory(self.drivetrain, [self.drivetrain.getPose(), Pose2d(0, 3, 90), Pose2d(3, 3, 0)], 0.5)
    """
    start_speed = autoproperty(0.1)
    accel = autoproperty(0.5)
    angle_factor = autoproperty(2.5)
    track_error_factor = autoproperty(3.0)

    @classmethod
    def toLoading(cls, drivetrain: Drivetrain):
        cmd = ConditionalCommand(
            cls(drivetrain, red_loading_pose, lambda: properties.to_loading_speed, origin="absolute"),
            cls(drivetrain, blue_loading_pose, lambda: properties.to_loading_speed, origin="absolute"),
            lambda: DriverStation.getAlliance() == DriverStation.Alliance.kRed
        )
        cmd.setName(cmd.getName() + ".toLoading")
        return cmd

    @classmethod
    def driveStraight(cls, drivetrain: Drivetrain, distance: float, speed: float):
        cmd = cls(drivetrain, Pose2d(distance, 0, 0), speed, origin="relative")
        cmd.setName(cmd.getName() + ".driveStraight")
        return cmd

    def __init__(
            self,
            drivetrain: Drivetrain,
            waypoints: Union[Pose2d, Iterable[Pose2d]],
            speed: FloatProperty,
            origin: Literal["absolute", "relative"],
            direction: Literal["forward", "backward"] = "forward"
    ) -> None:
        super().__init__()
        self.waypoints = waypoints if isinstance(waypoints, Iterable) else [waypoints]
        self.drivetrain = drivetrain
        self.addRequirements(drivetrain)
        self.speed = as_callable(speed)
        self.path_reversed = (direction == "backward")
        self.config = TrajectoryConfig(10, 10)
        self.config.setReversed(self.path_reversed)
        self.origin = origin
        self._delta = 0.0
        self._computed_speed = 0.0
        self._controller = None

        if self.origin == "relative":
            self.relative_trajectory = TrajectoryGenerator.generateTrajectory(
                [Pose2d(0, 0, 0), *self.waypoints],
                self.config
            )

    def initialize(self) -> None:
        if self.origin == "relative":
            self.trajectory = self.relative_trajectory.transformBy(Transform2d(Pose2d(), self.drivetrain.getPose()))
        else:
            self.trajectory = TrajectoryGenerator.generateTrajectory(
                [self.drivetrain.getPose(), *self.waypoints],
                self.config
            )

        self.motion = TrapezoidalMotion(
            min_speed=self.start_speed,
            max_speed=self.speed(),
            accel=self.accel,
            start_position=0,
            end_position=self.trajectory.totalTime()
        )
        self.drivetrain.getField().getObject("traj").setTrajectory(self.trajectory)
        self._controller = RearWheelFeedbackController(self.trajectory)

    def execute(self) -> None:
        current_pose = self.drivetrain.getPose()
        self._delta = self._controller.update(current_pose, self.angle_factor, self.track_error_factor)
        self.motion.setPosition(self._controller.closest_t)
        self._computed_speed = self.motion.getSpeed() * (-1 if self.path_reversed else 1)
        self.drivetrain.tankDrive(self._computed_speed - self._delta, self._computed_speed + self._delta)

    def isFinished(self) -> bool:
        return self._controller.closest_t >= 0.99 * self.trajectory.totalTime()

    def end(self, interrupted: bool) -> None:
        self.drivetrain.tankDrive(0, 0)

    def initSendable(self, builder: wpiutil.SendableBuilder) -> None:
        super().initSendable(builder)
        builder.addDoubleProperty("closest_t", lambda: self._controller.closest_t if self._controller else 0.0, default_setter)
        builder.addDoubleProperty("computed_speed", lambda: self._computed_speed, default_setter)
        builder.addDoubleProperty("delta", lambda: self._delta, default_setter)


class _ClassProperties:
    to_loading_speed = autoproperty(0.6, subtable=FollowTrajectory.__name__)


properties = _ClassProperties()
