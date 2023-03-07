import commands2
from wpimath.geometry import Pose2d

from commands.autonomous.autodrop import AutoDrop
from commands.drivetodock import DriveToDock
from commands.drop import Drop
from subsystems.drivetrain import Drivetrain
from subsystems.claw import Claw
from subsystems.arm import Arm
from commands.followtrajectory import FollowTrajectory
from utils.property import autoproperty

from commands.movearm import MoveArm
from commands.closeclaw import CloseClaw
from commands.openclaw import OpenClaw


class AutoDock(commands2.SequentialCommandGroup):
    backwards_distance = autoproperty(10.0)
    def __init__(self, drivetrain: Drivetrain, claw: Claw, arm: Arm, drop: bool):
        cmds = []

        if drop:
            cmds.append(AutoDrop(claw, arm))

        super().__init__(
            *cmds,
            DriveToDock(drivetrain, True)
        )