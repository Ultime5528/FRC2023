import commands2

from commands.autonomous.autodrop import AutoDrop
from commands.drivetodock import DriveToDock
from subsystems.drivetrain import Drivetrain
from subsystems.claw import Claw
from subsystems.arm import Arm
from utils.property import autoproperty


class AutoDock(commands2.SequentialCommandGroup):
    backwards_distance = autoproperty(10.0)

    def __init__(self, drivetrain: Drivetrain, claw: Claw, arm: Arm, drop: bool):
        commands = [DriveToDock(drivetrain, True)]
        if drop:
            commands.insert(0, AutoDrop(claw, arm))

        super().__init__(
            *commands
        )