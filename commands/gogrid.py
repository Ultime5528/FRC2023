from typing import Literal

from wpimath.geometry import Transform2d, Translation2d, Rotation2d
from commands2 import SequentialCommandGroup, ConditionalCommand
from commands.followtrajectory import FollowTrajectory
from commands.turn import Turn
from subsystems.drivetrain import Drivetrain, april_tag_field
from wpilib import DriverStation

red_left_offset = Transform2d(Translation2d(0.5, -0.47), Rotation2d.fromDegrees(180))
red_mid_offset = Transform2d(Translation2d(0.5, 0), Rotation2d.fromDegrees(180))
red_right_offset = Transform2d(Translation2d(0.5, 0.47), Rotation2d.fromDegrees(180))
blue_left_offset = Transform2d(Translation2d(0.5, -0.47), Rotation2d(0))
blue_mid_offset = Transform2d(Translation2d(0.5, 0), Rotation2d(0))
blue_right_offset = Transform2d(Translation2d(0.5, 0.47), Rotation2d(0))

# Numbers: left to right driver pov
red_poses = {
    "2": april_tag_field.getTagPose(1).toPose2d().transformBy(red_mid_offset),
    "1": april_tag_field.getTagPose(1).toPose2d().transformBy(red_right_offset),
    "3": april_tag_field.getTagPose(1).toPose2d().transformBy(red_left_offset),
    "5": april_tag_field.getTagPose(2).toPose2d().transformBy(red_mid_offset),
    "4": april_tag_field.getTagPose(2).toPose2d().transformBy(red_right_offset),
    "6": april_tag_field.getTagPose(2).toPose2d().transformBy(red_left_offset),
    "8": april_tag_field.getTagPose(3).toPose2d().transformBy(red_mid_offset),
    "7": april_tag_field.getTagPose(3).toPose2d().transformBy(red_right_offset),
    "9": april_tag_field.getTagPose(3).toPose2d().transformBy(red_left_offset),
}

blue_poses = {
    "2": april_tag_field.getTagPose(6).toPose2d().transformBy(blue_mid_offset),
    "1": april_tag_field.getTagPose(6).toPose2d().transformBy(blue_right_offset),
    "3": april_tag_field.getTagPose(6).toPose2d().transformBy(blue_left_offset),
    "5": april_tag_field.getTagPose(7).toPose2d().transformBy(blue_mid_offset),
    "4": april_tag_field.getTagPose(7).toPose2d().transformBy(blue_right_offset),
    "6": april_tag_field.getTagPose(7).toPose2d().transformBy(blue_left_offset),
    "8": april_tag_field.getTagPose(8).toPose2d().transformBy(blue_mid_offset),
    "7": april_tag_field.getTagPose(8).toPose2d().transformBy(blue_right_offset),
    "9": april_tag_field.getTagPose(8).toPose2d().transformBy(blue_left_offset),
}


class GoGrid(SequentialCommandGroup):
    def __init__(self, drivetrain: Drivetrain, grid_number: Literal["1", "2", "3", "4", "5", "6", "7", "8", "9"]):
        """
        Parameters
        ----------
        drivetrain
        Number of the grid cell from left to right
        """
        if DriverStation.getAlliance() == DriverStation.Alliance.kRed:
            grid_pos = red_poses[grid_number]
        else:
            grid_pos = blue_poses[grid_number]

        super().__init__(
                FollowTrajectory(drivetrain, grid_pos, 1, "absolute")
                )
