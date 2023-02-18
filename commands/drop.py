from subsystems.claw import Claw
from subsystems.arm import Arm

from commands.openclaw import OpenClaw
from commands.movearm import MoveArm

from commands2 import SequentialCommandGroup

from utils.safecommand import SafeMixin


class Drop(SafeMixin, SequentialCommandGroup):
    def __init__(self, claw: Claw, arm: Arm):
        super().__init__(
            OpenClaw(claw),
            MoveArm.toBase(arm)
        )
