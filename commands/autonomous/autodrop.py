import commands2
from wpimath.geometry import Pose2d

from commands.drop import Drop
from commands.resetarm import ResetArm
from subsystems.drivetrain import Drivetrain
from subsystems.claw import Claw
from subsystems.arm import Arm
from commands.followtrajectory import FollowTrajectory
from utils.property import autoproperty

from commands.movearm import MoveArm
from commands.closeclaw import CloseClaw
from commands.openclaw import OpenClaw
from utils.safecommand import SafeMixin


class AutoDrop(SafeMixin, commands2.SequentialCommandGroup):
    def __init__(self, claw: Claw, arm: Arm):
        super().__init__(
            ResetArm(arm),
            MoveArm.toLevel3(arm),  # Niveau trois
            Drop(claw, arm),  # Déposer
        )