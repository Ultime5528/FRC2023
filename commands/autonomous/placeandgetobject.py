import commands2
import wpilib

from commands.autonomous import redplaceandgetobject, blueplaceandgetobject
from subsystems.arm import Arm
from subsystems.claw import Claw
from subsystems.drivetrain import Drivetrain
from utils.safecommand import SafeCommand


class PlaceAndGetObject(commands2.ConditionalCommand):
    def __init__(self, drivetrain: Drivetrain, claw: Claw, arm: Arm):
        super().__init__(blueplaceandgetobject.BluePlaceAndGetObject(drivetrain, claw, arm),
                         redplaceandgetobject.RedPlaceAndGetObject(drivetrain, claw, arm),
                         lambda: wpilib.DriverStation.getAlliance() == wpilib.DriverStation.Alliance.kBlue)
