import rev
import wpilib
import wpiutil
from wpilib import DigitalInput, RobotBase
from wpilib.simulation import DIOSim

import ports
from utils.property import autoproperty
from utils.safesubsystem import SafeSubsystem
from utils.sparkmaxsim import SparkMaxSim


def checkIsInDeadzoneUpper(extension: float, elevation: float):
    return extension >= properties.deadzone_upper_extension and elevation >= properties.deadzone_upper_elevation


def checkIsInDeadzoneLower(extension:  float, elevation:  float):
    return extension <= properties.deadzone_lower_extension and elevation <= properties.deadzone_lower_elevation


class Arm(SafeSubsystem):
    extension_max_position = autoproperty(10.0)
    elevator_max_position = autoproperty(10.0)

    def __init__(self):
        super().__init__()

        # Switches
        self.switch_extension_min = DigitalInput(ports.arm_switch_extension_min)
        self.addChild("switch_extension_min", self.switch_extension_min)

        self.switch_extension_max = DigitalInput(ports.arm_switch_extension_max)
        self.addChild("switch_extension_max", self.switch_extension_max)

        self.switch_elevator_max = DigitalInput(ports.arm_switch_elevator_max)
        self.addChild("switch_elevator_max", self.switch_elevator_max)

        # Motors
        self.motor_elevator = rev.CANSparkMax(ports.arm_motor_elevator,
                                              rev.CANSparkMax.MotorType.kBrushless)

        self.motor_extension = rev.CANSparkMax(ports.arm_motor_extension,
                                               rev.CANSparkMax.MotorType.kBrushless)

        self.encoder_extension = self.motor_extension.getEncoder()
        self.encoder_elevator = self.motor_elevator.getEncoder()

        self.photocell = wpilib.DigitalInput(ports.photocell)
        self.addChild("photocell", self.photocell)

        self._extension_offset = 0.0
        self._elevator_offset = 0.0

        if RobotBase.isSimulation():
            self.motor_elevator_sim = SparkMaxSim(self.motor_elevator)
            self.motor_extension_sim = SparkMaxSim(self.motor_extension)
            self.switch_extension_min_sim = DIOSim(self.switch_extension_min)
            self.switch_extension_max_sim = DIOSim(self.switch_extension_max)
            self.switch_elevator_max_sim = DIOSim(self.switch_elevator_max)

    def simulationPeriodic(self):
        motor_elevator_sim_increment = self.motor_elevator.get() * 0.5
        motor_extension_sim_increment = self.motor_extension.get() * 0.5
        self.motor_elevator_sim.setPosition(self.motor_elevator_sim.getPosition() + motor_elevator_sim_increment)
        self.motor_extension_sim.setPosition(self.motor_extension_sim.getPosition() + motor_extension_sim_increment)
        self.switch_extension_min_sim.setValue(self.getExtensionPosition() <= 0.05)
        self.switch_elevator_max_sim.setValue(self.getElevatorPosition() >= self.elevator_max_position - 0.05)
        self.switch_extension_max_sim.setValue(self.getExtensionPosition() >= self.extension_max_position - 0.05)

    def periodic(self):
        if self.switch_extension_min.get():
            self._extension_offset = self.encoder_extension.getPosition()  # Reset to zero
        if self.switch_extension_max.get():
            self._extension_offset = self.encoder_extension.getPosition() - self.extension_max_position
        if self.switch_elevator_max.get():
            self._elevator_offset = self.encoder_elevator.getPosition() - self.elevator_max_position

    def getElevatorPosition(self):
        return self.encoder_elevator.getPosition() - self._elevator_offset

    def getExtensionPosition(self):
        return self.encoder_elevator.getPosition() - self._extension_offset

    def setElevatorSpeed(self, speed: float):
        self.motor_elevator.set(speed)

    def setExtensionSpeed(self, speed: float):
        self.motor_extension.set(speed)

    def isInDeadzoneUpper(self):
        return checkIsInDeadzoneUpper(self.getExtensionPosition(), self.getElevatorPosition())

    def isInDeadzoneLower(self):
        return checkIsInDeadzoneLower(self.getExtensionPosition(), self.getElevatorPosition())

    def shouldTransition(self, extension:  float, elevation:  float):
        return self.isInDeadzoneUpper() and checkIsInDeadzoneLower(extension, elevation) or \
               self.isInDeadzoneLower() and checkIsInDeadzoneUpper(extension, elevation)

    def initSendable(self, builder: wpiutil.SendableBuilder) -> None:
        super().initSendable(builder)
        builder.addDoubleProperty("Elevator position", self.getElevatorPosition, None)
        builder.addDoubleProperty("Extension position", self.getExtensionPosition, None)

    def getPhotocell(self):
        return self.photocell.get()


class _ClassProperties:
    deadzone_lower_extension = autoproperty(0, subtable=Arm.__name__)
    deadzone_lower_elevation = autoproperty(0, subtable=Arm.__name__)
    deadzone_upper_extension = autoproperty(0, subtable=Arm.__name__)
    deadzone_upper_elevation = autoproperty(0, subtable=Arm.__name__)


properties = _ClassProperties()
