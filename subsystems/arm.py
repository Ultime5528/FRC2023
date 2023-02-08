import rev
import wpilib
from wpilib import DigitalInput, RobotBase
from wpilib.simulation import DIOSim

import ports
from utils.safesubsystem import SafeSubsystem
from utils.sparkmaxsim import SparkMaxSim


class Arm(SafeSubsystem):
    def __init__(self):
        super().__init__()

        # Switches
        self.switch_extension_min = DigitalInput(ports.arm_switch_extension_min)
        self.addChild("switch_extension_min", self.switch_extension_min)

        self.switch_extension_max = DigitalInput(ports.arm_switch_extension_max)
        self.addChild("switch_extension_max", self.switch_extension_max)

        self.switch_elevator_min = DigitalInput(ports.arm_switch_elevator_min)
        self.addChild("switch_elevator_min", self.switch_elevator_min)

        self.switch_elevator_max = DigitalInput(ports.arm_switch_elevator_max)
        self.addChild("switch_elevator_max", self.switch_elevator_max)

        # Motors
        self.motor_elevator = rev.CANSparkMax(ports.arm_motor_elevator,
                                              rev.CANSparkMax.MotorType.kBrushless)

        self.motor_extension = rev.CANSparkMax(ports.arm_motor_extension,
                                               rev.CANSparkMax.MotorType.kBrushless)

        self.encoder_extension = self.motor_extension.getEncoder()
        self.encoder_elevator = self.motor_elevator.getEncoder()

        if RobotBase.isSimulation():
            self.motor_elevator_sim = SparkMaxSim(self.motor_elevator)
            self.motor_extension_sim = SparkMaxSim(self.motor_extension)
            self.switch_extension_min_sim = DIOSim(self.switch_extension_min)
            self.switch_extension_max_sim = DIOSim(self.switch_extension_max)
            self.switch_elevator_min_sim = DIOSim(self.switch_elevator_min)
            self.switch_elevator_max_sim = DIOSim(self.switch_elevator_max)

    def simulationPeriodic(self):
        motor_elevator_sim_increment = self.motor_elevator.get() * 0.1
        motor_extension_sim_increment = self.motor_extension.get() * 0.1
        self.motor_elevator_sim.setPosition(self.motor_elevator_sim.getPosition() + motor_elevator_sim_increment)
        self.motor_extension_sim.setPosition(self.motor_extension_sim.getPosition() + motor_extension_sim_increment)
        self.switch_elevator_min_sim.setValue(self.getElevatorPosition() <= 0.05)
        self.switch_extension_min_sim.setValue(self.getExtensionPosition() <= 0.05)
        self.switch_elevator_max_sim.setValue(self.getElevatorPosition() >= 9.95)
        self.switch_extension_max_sim.setValue(self.getExtensionPosition() >= 9.95)

    def periodic(self):
        if self.switch_extension_min.get():  # encoder.setPosition does not work
            self.encoder_extension.setPosition(0)
        if self.switch_elevator_min.get():
            self.encoder_elevator.setPosition(0)
        if self.switch_extension_max.get():
            self.encoder_extension.setPosition(10)  # todo change to a better value
        if self.switch_elevator_max.get():
            self.encoder_elevator.setPosition(10)

    def getElevatorPosition(self):
        return self.encoder_elevator.getPosition()

    def getExtensionPosition(self):
        return self.encoder_elevator.getPosition()

    def setElevatorSpeed(self, speed: float):
        # if RobotBase.isSimulation():
        #     self.motor_elevator_sim.setPosition(speed)
        self.motor_elevator.set(speed)

    def setExtensionSpeed(self, speed: float):
        # if RobotBase.isSimulation():
        #     self.motor_extension_sim.setPosition(speed)
        self.motor_extension.set(speed)
