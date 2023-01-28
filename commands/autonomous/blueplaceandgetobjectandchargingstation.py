import commands2
from wpimath.geometry import Pose2d

from subsystems.drivetrain import Drivetrain
from subsystems.claw import Claw
from subsystems.arm import Arm
from commands.followtrajectory import FollowTrajectory

from commands.movearm import MoveArm
from commands.closeclaw import CloseClaw
from commands.openclaw import OpenClaw


class BluePlaceAndGetObjectAndChargingStation(commands2.SequentialCommandGroup):
    def __init__(self, drivetrain: Drivetrain, claw: Claw, arm: Arm):
        super().__init__(
            MoveArm.toThirdLevel(arm),
            OpenClaw(claw),
            commands2.ParallelCommandGroup(
                FollowTrajectory(drivetrain, [Pose2d(5.69, 0.92, 0)], 0.75, origin="absolute"),
                MoveArm.toPickupLevel(arm),
            ),
            CloseClaw(claw),
            FollowTrajectory(drivetrain, [Pose2d(2.74, 0.51, 0)], 0.75, origin="absolute", direction="backward")
        )