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

        self.switch_elevator_min = DigitalInput(ports.arm_switch_elevator_min)
        self.addChild("switch_elevator_min", self.switch_elevator_min)

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
            self.switch_elevator_min_sim = DIOSim(self.switch_elevator_min)

    def getElevatorPosition(self):
        return self.encoder_elevator.getPosition()

    def getExtensionPosition(self):
        return self.encoder_elevator.getPosition()

    def setElevatorSpeed(self, speed: float):
        if RobotBase.isSimulation():
            self.motor_elevator_sim.setPosition(speed)
        self.motor_elevator.set(speed)

    def setExtensionSpeed(self, speed: float):
        if RobotBase.isSimulation():
            self.motor_extension_sim.setPosition(speed)
        self.motor_elevator.set(speed)
