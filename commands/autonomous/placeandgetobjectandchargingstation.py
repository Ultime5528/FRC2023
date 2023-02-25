import commands2
import wpilib

from commands.autonomous import blueplaceandgetobject, redplaceandgetobject, redplaceandgetobjectandchargingstation, \
    blueplaceandgetobjectandchargingstation
from subsystems.arm import Arm
from subsystems.claw import Claw
from subsystems.drivetrain import Drivetrain


class PlaceAndGetObjectAndChargingStation(commands2.SequentialCommandGroup):
    def __init__(self, drivetrain: Drivetrain, claw: Claw, arm: Arm):
        if wpilib.DriverStation.getAlliance() == wpilib.DriverStation.Alliance.kRed:
            super().__init__(redplaceandgetobjectandchargingstation.RedPlaceAndGetObjectAndChargingStation(drivetrain, claw, arm))
        elif wpilib.DriverStation.getAlliance() == wpilib.DriverStation.Alliance.kBlue:
            super().__init__(blueplaceandgetobjectandchargingstation.BluePlaceAndGetObjectAndChargingStation(drivetrain, claw, arm))
