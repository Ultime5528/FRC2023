import commands2

from commands.drop import Drop
from commands.resetarm import ResetArm
from subsystems.claw import Claw
from subsystems.arm import Arm

from commands.movearm import MoveArm
from commands.closeclaw import CloseClaw
from utils.safecommand import SafeMixin


class AutoDrop(SafeMixin, commands2.SequentialCommandGroup):
    def __init__(self, claw: Claw, arm: Arm):
        super().__init__(
            ResetArm(arm),
            CloseClaw(claw).withTimeout(1.0),
            MoveArm.toLevel3(arm),  # Niveau trois
            Drop(claw, arm),  # Déposer
        )
