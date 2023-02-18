import rev
import wpilib
import wpiutil
from wpilib import DigitalInput, RobotBase
from wpilib.simulation import DIOSim

import ports
from utils.property import autoproperty, default_setter
from utils.safesubsystem import SafeSubsystem
from utils.sparkmaxsim import SparkMaxSim
from utils.sparkmaxutils import configure_leader


def checkIsInDeadzone(extension: float):
    return extension <= properties.deadzone_extension


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

        self.switch_elevator_min = DigitalInput(ports.arm_switch_elevator_min)
        self.addChild("switch_elevator_min", self.switch_elevator_min)

        # Motors
        self.motor_elevator = rev.CANSparkMax(ports.arm_motor_elevator,
                                              rev.CANSparkMax.MotorType.kBrushless)
        configure_leader(self.motor_elevator, "brake", True)

        self.motor_extension = rev.CANSparkMax(ports.arm_motor_extension,
                                               rev.CANSparkMax.MotorType.kBrushless)
        configure_leader(self.motor_extension, "brake", True)

        self.encoder_extension = self.motor_extension.getEncoder()
        self.encoder_elevator = self.motor_elevator.getEncoder()

        self._extension_offset = 0.0
        self._elevator_offset = 0.0

        if RobotBase.isSimulation():
            self.motor_elevator_sim = SparkMaxSim(self.motor_elevator)
            self.motor_extension_sim = SparkMaxSim(self.motor_extension)
            self.switch_extension_min_sim = DIOSim(self.switch_extension_min)
            self.switch_extension_max_sim = DIOSim(self.switch_extension_max)
            self.switch_elevator_min_sim = DIOSim(self.switch_elevator_min)

    def simulationPeriodic(self):
        motor_elevator_sim_increment = self.motor_elevator.get() * 0.5
        motor_extension_sim_increment = self.motor_extension.get() * 0.5
        self.motor_elevator_sim.setPosition(self.motor_elevator_sim.getPosition() + motor_elevator_sim_increment)
        self.motor_extension_sim.setPosition(self.motor_extension_sim.getPosition() + motor_extension_sim_increment)
        self.switch_elevator_min_sim.setValue(self.getElevatorPosition() <= 0.05)
        self.switch_extension_min_sim.setValue(self.getExtensionPosition() <= 0.05)

    def periodic(self):
        if self.isExtensionMin():
            self._extension_offset = self.encoder_extension.getPosition()  # Reset to zero
        if self.isElevationMin():
            self._elevator_offset = self.encoder_elevator.getPosition()  # Reset to zero
        if self.isExtensionMax():
            self._extension_offset = self.encoder_extension.getPosition() - self.extension_max_position

    def isExtensionMin(self):
        return not self.switch_extension_min.get()

    def isExtensionMax(self):
        return not self.switch_extension_max.get()

    def isElevationMin(self):
        return not self.switch_elevator_min.get()

    def getElevatorPosition(self):
        return self.encoder_elevator.getPosition() - self._elevator_offset

    def getExtensionPosition(self):
        return self.encoder_extension.getPosition() - self._extension_offset

    def setElevatorSpeed(self, speed: float):
        self.motor_elevator.set(0 if self.isElevationMin() else speed)

    def setExtensionSpeed(self, speed: float):
        self.motor_extension.set(0 if self.isExtensionMin() or self.isExtensionMax() else speed)

    def isInDeadzone(self):
        return checkIsInDeadzone(self.getExtensionPosition())

    def shouldTransition(self, extension:  float, elevation:  float):
        return self.isInDeadzone() or checkIsInDeadzone(extension)

    def initSendable(self, builder: wpiutil.SendableBuilder) -> None:
        super().initSendable(builder)
        builder.addDoubleProperty("Elevator position", self.getElevatorPosition, default_setter)
        builder.addDoubleProperty("Extension position", self.getExtensionPosition, default_setter)


class _ClassProperties:
    deadzone_extension = autoproperty(0, subtable=Arm.__name__)


properties = _ClassProperties()
