from math import degrees, atan2
from typing import Literal
from wpimath.geometry import Transform2d, Translation2d, Rotation2d
from commands2 import SequentialCommandGroup, ConditionalCommand
from utils.safecommand import SafeCommand
from commands.followtrajectory import FollowTrajectory
from commands.turn import Turn
from subsystems.drivetrain import Drivetrain, april_tag_field
from wpilib import DriverStation

left_offset = Transform2d(Translation2d(0.5, -0.47), Rotation2d.fromDegrees(180))
mid_offset = Transform2d(Translation2d(0.5, 0), Rotation2d.fromDegrees(180))
right_offset = Transform2d(Translation2d(0.5, 0.47), Rotation2d.fromDegrees(180))

# Numbers: left to right driver pov
red_poses = {
    "2": april_tag_field.getTagPose(1).toPose2d().transformBy(mid_offset),
    "1": april_tag_field.getTagPose(1).toPose2d().transformBy(right_offset),
    "3": april_tag_field.getTagPose(1).toPose2d().transformBy(left_offset),
    "5": april_tag_field.getTagPose(2).toPose2d().transformBy(mid_offset),
    "4": april_tag_field.getTagPose(2).toPose2d().transformBy(right_offset),
    "6": april_tag_field.getTagPose(2).toPose2d().transformBy(left_offset),
    "8": april_tag_field.getTagPose(3).toPose2d().transformBy(mid_offset),
    "7": april_tag_field.getTagPose(3).toPose2d().transformBy(right_offset),
    "9": april_tag_field.getTagPose(3).toPose2d().transformBy(left_offset),
}

blue_poses = {
    "2": april_tag_field.getTagPose(6).toPose2d().transformBy(mid_offset),
    "1": april_tag_field.getTagPose(6).toPose2d().transformBy(right_offset),
    "3": april_tag_field.getTagPose(6).toPose2d().transformBy(left_offset),
    "5": april_tag_field.getTagPose(7).toPose2d().transformBy(mid_offset),
    "4": april_tag_field.getTagPose(7).toPose2d().transformBy(right_offset),
    "6": april_tag_field.getTagPose(7).toPose2d().transformBy(left_offset),
    "8": april_tag_field.getTagPose(8).toPose2d().transformBy(mid_offset),
    "7": april_tag_field.getTagPose(8).toPose2d().transformBy(right_offset),
    "9": april_tag_field.getTagPose(8).toPose2d().transformBy(left_offset),
}


class GoGrid(SafeCommand):
    def __init__(self, drivetrain: Drivetrain, grid_number: Literal["1", "2", "3", "4", "5", "6", "7", "8", "9"]):
        """
        Parameters
        ----------
        drivetrain
        Number of the grid cell from left to right
        """
        super().__init__()
        self.drivetrain = drivetrain
        self.grid_number = grid_number

    def initialize(self) -> None:
        if DriverStation.getAlliance() == DriverStation.Alliance.kRed:
            grid_pos = red_poses[self.grid_number]
        else:
            grid_pos = blue_poses[self.grid_number]

        robot_to_grid = Transform2d(self.drivetrain.getPose(), grid_pos)
        robot_to_grid_angle = degrees(atan2(robot_to_grid.Y(), robot_to_grid.X()))

        go_grid = SequentialCommandGroup(
            Turn(self.drivetrain, robot_to_grid_angle, 0.3),
            FollowTrajectory(self.drivetrain, grid_pos, 0.5, "absolute"),
            FollowTrajectory.driveStraight(self.drivetrain, 0.3, 0.5)
        )
        go_grid.setName("Go grid")
        go_grid.schedule()

    def isFinished(self) -> bool:
        return True