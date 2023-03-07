import commands2
from wpimath.geometry import Pose2d

from subsystems.drivetrain import Drivetrain
from subsystems.claw import Claw
from subsystems.arm import Arm
from commands.followtrajectory import FollowTrajectory

from commands.autonomous.autodrop import AutoDrop
from commands.movearm import MoveArm
from commands.closeclaw import CloseClaw
from commands.openclaw import OpenClaw
from commands.turn import Turn
from utils.safecommand import SafeMixin


class AutoLine(SafeMixin, commands2.SequentialCommandGroup):
    def __init__(self, drivetrain: Drivetrain, claw: Claw, arm: Arm, drop_object: bool):
        commands = [FollowTrajectory(drivetrain, Pose2d(-4.36, 0, 0), -1, "relative", "backward"), Turn(drivetrain, 180, 0.2)]
        if drop_object:
            commands.insert(0, AutoDrop(claw, arm))
        super().__init__(
            commands
        )