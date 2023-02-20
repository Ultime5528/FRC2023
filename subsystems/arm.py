import rev
import wpiutil
from wpilib import DigitalInput, RobotBase
from wpilib.event import EventLoop, BooleanEvent
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
    extension_min_position = autoproperty(-10.0)
    elevator_max_position = autoproperty(10.0)
    elevator_min_position = autoproperty(-10.0)


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

        self.loop = EventLoop()
        self._min_elevation_event = BooleanEvent(
            self.loop, self.isSwitchElevationMinOn
        ).rising()
        self._min_elevation_event.ifHigh(self.resetElevation)

        self._min_extension_event = BooleanEvent(
            self.loop, self.isSwitchExtensionMinOn
        ).rising()
        self._min_extension_event.ifHigh(self.resetExtension)

        self._max_extension_event = BooleanEvent(
            self.loop, self.isSwitchExtensionMaxOn
        ).rising()
        # self._max_extension_event.ifHigh(self.maximizeExtension)

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
        self.switch_extension_max_sim.setvalue(self.getExtensionPosition() >= self.extension_max_position)

    def periodic(self):
        self.loop.poll()

    def resetExtension(self):
        self._extension_offset = self.encoder_extension.getPosition()

    def resetElevation(self):
        self._elevator_offset = self.encoder_elevator.getPosition()

    # def maximizeExtension(self):
    #     self._extension_offset = self.encoder_extension.getPosition() - self.extension_max_position

    def getElevatorPosition(self):
        return self.encoder_elevator.getPosition() - self._elevator_offset

    def getExtensionPosition(self):
        return self.encoder_extension.getPosition() - self._extension_offset

    def isSwitchExtensionMinOn(self):
        return not self.switch_extension_min.get()

    def isSwitchExtensionMaxOn(self):
        return not self.switch_extension_max.get()

    def isSwitchElevationMinOn(self):
        return not self.switch_elevator_min.get()

    def isPositionExtensionMax(self):
        return self.getExtensionPosition() > self.extension_max_position

    def isPositionExtensionMin(self):
        return self.getExtensionPosition() < self.extension_min_position

    def isPositionElevationMax(self):
        return self.getElevationPosition() > self.elevation_max_position

    def isPositionElevationMax(self):
        return self.getElevationPosition() < self.elevation_min_position

    def setElevatorSpeed(self, speed: float):
        if self.isElevationMin() and speed < 0:
            speed = 0
        if self.isElevationMax() and speed > 0:
            speed = 0
        self.motor_elevator.set(speed)

    def setExtensionSpeed(self, speed: float):
        if self.isExtensionMin() and speed < 0:
            speed = 0
        if self.isExtensionMax() and speed > 0:
            speed = 0
        self.motor_extension.set(speed)

    def isInDeadzone(self):
        return checkIsInDeadzone(self.getExtensionPosition())

    def shouldTransition(self, extension:  float, elevation:  float):
        return self.isInDeadzone() or checkIsInDeadzone(extension)

    def initSendable(self, builder: wpiutil.SendableBuilder) -> None:
        super().initSendable(builder)
        builder.addDoubleProperty("Elevator position", self.getElevatorPosition, default_setter)
        builder.addDoubleProperty("Extension position", self.getExtensionPosition, default_setter)


class _ClassProperties:
    deadzone_extension = autoproperty(1.0, subtable=Arm.__name__)


properties = _ClassProperties()
