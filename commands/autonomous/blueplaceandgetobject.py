import commands2
from wpimath.geometry import Pose2d

from subsystems.drivetrain import Drivetrain
from subsystems.claw import Claw
from subsystems.arm import Arm
from commands.followtrajectory import FollowTrajectory

from commands.movearm import MoveArm
from commands.closeclaw import CloseClaw
from commands.openclaw import OpenClaw


class BluePlaceAndGetObject(commands2.SequentialCommandGroup):
    def __init__(self, drivetrain: Drivetrain, claw: Claw, arm: Arm):
        super().__init__(
            MoveArm.toLevel3(arm),# Niveau trois
            OpenClaw(claw),# Déposer
            commands2.ParallelCommandGroup(
                FollowTrajectory(drivetrain, [Pose2d(6.265738, 0.785636, 0)], 0.75, origin="absolute"),# Aller milieu (où les 4 objets de choix)
                MoveArm.toFloor(arm),# Préparer à prendre objet
            ),
            CloseClaw(claw), # Prendre objet
            FollowTrajectory(drivetrain, [Pose2d(1.930974, 0.894436, 0)], 0.75, origin="absolute", direction="backward")# Aller à drop
        )