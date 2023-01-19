import math
from typing import Literal

import navx
import rev
import wpilib
import wpilib.drive
from wpilib import RobotBase, RobotController
from wpilib.simulation import DifferentialDrivetrainSim, SimDeviceSim
from wpimath.geometry import Pose2d, Rotation2d
from wpimath.kinematics import DifferentialDriveOdometry
from wpimath.system import LinearSystemId
from wpimath.system.plant import DCMotor

from gyro import NavX, ADIS, ADXRS, Empty
from utils.sparkmaxutils import configure_follower, configure_leader
from utils.safesubsystembase import SafeSubsystemBase
from utils.sparkmaxsim import SparkMaxSim
import ports

select_gyro: Literal["navx", "adis", "adxrs", "empty"] = "navx"


class Drivetrain(SafeSubsystemBase):

    def __init__(self) -> None:
        super().__init__()
        # Motors
        self._motor_left = rev.CANSparkMax(ports.drivetrain_motor_front_left, rev.CANSparkMax.MotorType.kBrushless)
        configure_leader(self._motor_left, "brake")

        self._motor_left_follower = rev.CANSparkMax(ports.drivetrain_motor_rear_left,
                                                    rev.CANSparkMax.MotorType.kBrushless)
        configure_follower(self._motor_left_follower, self._motor_left, "brake")

        self._motor_right = rev.CANSparkMax(ports.drivetrain_motor_front_right,
                                            rev.CANSparkMax.MotorType.kBrushless)
        configure_leader(self._motor_right, "brake")
        self._motor_right_follower = rev.CANSparkMax(ports.drivetrain_motor_rear_right,
                                                     rev.CANSparkMax.MotorType.kBrushless)
        configure_follower(self._motor_right_follower, self._motor_right, "brake")


        self._drive = wpilib.drive.DifferentialDrive(self._motor_left, self._motor_right)
        self.addChild("DifferentialDrive", self._drive)

        # Odometry
        self._encoder_left = self._motor_left.getEncoder()
        self._encoder_right = self._motor_right.getEncoder()
        self._encoder_left.setPositionConversionFactor(0.0463)
        self._encoder_right.setPositionConversionFactor(0.0463)

        self._gyro = {
            "navx": NavX,
            "adis": ADIS,
            "adxrs": ADXRS,
            "empty": Empty,
        }[select_gyro]()
        self._odometry = DifferentialDriveOdometry(self._gyro.getRotation2d(), 0, 0, initialPose=Pose2d(5, 5, 0))
        
        self._field = wpilib.Field2d()
        wpilib.SmartDashboard.putData("Field", self._field)
        self._left_encoder_offset = 0
        self._right_encoder_offset = 0

        if hasattr(self._gyro, "gyro"):
            self.addChild("Gyro", self._gyro.gyro)

        if RobotBase.isSimulation():
            self._motor_left_sim = SparkMaxSim(self._motor_left)
            self._motor_right_sim = SparkMaxSim(self._motor_right)
            self._system = LinearSystemId.identifyDrivetrainSystem(1.98, 0.2, 5, 0.3)
            self._drive_sim = DifferentialDrivetrainSim(self._system, 0.64, DCMotor.NEO(4), 1.5, 0.08, [
                0.001, 0.001, 0.001, 0.1, 0.1, 0.005, 0.005
            ])

    def arcadeDrive(self, forward: float, rotation: float) -> None:
        self._drive.arcadeDrive(forward, rotation, False)

    def tankDrive(self, left: float, right: float) -> None:
        self._drive.tankDrive(left, right, False)

    def simulationPeriodic(self):
        self._drive_sim.setInputs(
            self._motor_left.get() * RobotController.getInputVoltage(),
            self._motor_right.get() * RobotController.getInputVoltage())
        self._drive_sim.update(0.02)
        self._motor_left_sim.setPosition(self._drive_sim.getLeftPosition() + self._left_encoder_offset)
        self._motor_left_sim.setVelocity(self._drive_sim.getLeftVelocity())
        self._motor_right_sim.setPosition(-self._drive_sim.getRightPosition() + self._right_encoder_offset)
        self._motor_right_sim.setVelocity(self._drive_sim.getRightVelocity())
        self._gyro_sim.set(-self._drive_sim.getHeading().degrees())

    def resetOdometry(self) -> None:
        self._left_encoder_offset = self._encoder_left.getPosition()
        self._right_encoder_offset = self._encoder_right.getPosition()
        self._odometry.resetPosition(Pose2d(), Rotation2d.fromDegrees(0.0))

        if RobotBase.isSimulation():
            self._drive_sim.setPose(Pose2d())
        else:
            self._gyro.reset()

    def getAngle(self):
        return self._gyro.getAngle()

    def getLeftEncoderPosition(self):
        return self._encoder_left.getPosition() - self._left_encoder_offset

    def getRightEncoderPosition(self):
        return -(self._encoder_right.getPosition() - self._right_encoder_offset)

    def getAverageEncoderPosition(self):
        return (self.getLeftEncoderPosition() + self.getRightEncoderPosition()) / 2

    def getPose(self):
        return self._odometry.getPose()

    def getField(self):
        return self._field

    def periodic(self):
        self._odometry.update(self._gyro.getRotation2d(), self.getLeftEncoderPosition(), self.getRightEncoderPosition())
        self._field.setRobotPose(self._odometry.getPose())
        wpilib.SmartDashboard.putNumber("Left Encoder Position", self.getLeftEncoderPosition())
        wpilib.SmartDashboard.putNumber("Right Encoder Position", self.getRightEncoderPosition())
        wpilib.SmartDashboard.putNumber("Left Motor", self._motor_left.get())
        wpilib.SmartDashboard.putNumber("Right Motor", self._motor_right.get())