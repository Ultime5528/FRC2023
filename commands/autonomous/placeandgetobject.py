import commands2
import wpilib

from commands.autonomous.redplaceandgetobject import RedPlaceAndGetObject
from commands.autonomous.blueplaceandgetobject import BluePlaceAndGetObject
from subsystems.arm import Arm
from subsystems.claw import Claw
from subsystems.drivetrain import Drivetrain
from utils.safecommand import SafeCommand


class PlaceAndGetObject(SafeCommand):
    def __init__(self, drivetrain: Drivetrain, claw: Claw, arm: Arm):
        super().__init__()
        self.drivetrain = drivetrain
        self.claw = claw
        self.arm = arm

    def execute(self) -> None:
        if wpilib.DriverStation.getAlliance() == wpilib.DriverStation.Alliance.kRed:
            RedPlaceAndGetObject(self.drivetrain, self.claw, self.arm)
        elif wpilib.DriverStation.getAlliance() == wpilib.DriverStation.Alliance.kBlue:
            BluePlaceAndGetObject(self.drivetrain, self.claw, self.arm)

    def isFinished(self) -> bool:
        return True
