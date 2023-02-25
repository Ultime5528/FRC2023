import commands2
import wpilib

from commands.autonomous import blueplaceandgetobject, redplaceandgetobject
from subsystems.arm import Arm
from subsystems.claw import Claw
from subsystems.drivetrain import Drivetrain


class PlaceAndGetObject(commands2.SequentialCommandGroup):
    def __init__(self, drivetrain: Drivetrain, claw: Claw, arm: Arm):
        if wpilib.DriverStation.getAlliance() == wpilib.DriverStation.Alliance.kRed:
            super().__init__(redplaceandgetobject.RedPlaceAndGetObject(drivetrain, claw, arm))
        elif wpilib.DriverStation.getAlliance() == wpilib.DriverStation.Alliance.kBlue:
            super().__init__(blueplaceandgetobject.BluePlaceAndGetObject(drivetrain, claw, arm))
