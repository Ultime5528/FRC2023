import commands2
import wpilib

from commands.autonomous import redplaceandgetobjectandchargingstation, blueplaceandgetobjectandchargingstation
from subsystems.arm import Arm
from subsystems.claw import Claw
from subsystems.drivetrain import Drivetrain
from utils.safecommand import SafeCommand


class PlaceAndGetObjectAndChargingStation(commands2.ConditionalCommand):
    def __init__(self, drivetrain: Drivetrain, claw: Claw, arm: Arm):
        super().__init__(blueplaceandgetobjectandchargingstation.BluePlaceAndGetObjectAndChargingStation(drivetrain, claw, arm),
                         redplaceandgetobjectandchargingstation.RedPlaceAndGetObjectAndChargingStation(drivetrain, claw, arm),
                         lambda: wpilib.DriverStation.getAlliance() == wpilib.DriverStation.Alliance.kBlue)
