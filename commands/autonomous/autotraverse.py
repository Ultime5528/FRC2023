
import commands2

from commands.autonomous.autodrop import AutoDrop
from commands.traversedock import TraverseDock
from subsystems.drivetrain import Drivetrain
from subsystems.claw import Claw
from subsystems.arm import Arm


class AutoTraverse(commands2.SequentialCommandGroup):
    def __init__(self, drivetrain: Drivetrain, claw: Claw, arm: Arm, drop: bool):
        commands = [TraverseDock(drivetrain)]

        if drop:
            commands.insert(0, AutoDrop(claw, arm))

        super().__init__(
            *commands
        )