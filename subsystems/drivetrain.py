from typing import Literal

import rev
import wpilib
from photonvision import PhotonCamera, SimVisionSystem, SimVisionTarget
from robotpy_apriltag import AprilTagField, loadAprilTagLayoutField
from wpilib import RobotBase, RobotController
from wpilib import drive, DriverStation
from wpilib.simulation import DifferentialDrivetrainSim
from wpimath.estimator import DifferentialDrivePoseEstimator
from wpimath.geometry import Pose2d, Rotation3d, Translation3d, Transform3d
from wpimath.kinematics import DifferentialDriveKinematics
from wpimath.system import LinearSystemId
from wpimath.system.plant import DCMotor

import ports
from gyro import NavX, ADIS, ADXRS, Empty
from utils.safesubsystembase import SafeSubsystemBase
from utils.sparkmaxsim import SparkMaxSim
from utils.sparkmaxutils import configure_follower, configure_leader

select_gyro: Literal["navx", "adis", "adxrs", "empty"] = "navx"
april_tag_field = loadAprilTagLayoutField(AprilTagField.k2023ChargedUp)


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

        # Photon Vision
        self.latest = None

        # Encoders
        self._encoder_left = self._motor_left.getEncoder()
        self._encoder_right = self._motor_right.getEncoder()
        self._encoder_left.setPositionConversionFactor(0.0463)
        self._encoder_right.setPositionConversionFactor(0.0463)
        self._left_encoder_offset = 0
        self._right_encoder_offset = 0

        # Gyro
        self._gyro = {
            "navx": NavX,
            "adis": ADIS,
            "adxrs": ADXRS,
            "empty": Empty,
        }[select_gyro]()

        # Odometry
        self._kinematics = DifferentialDriveKinematics(trackWidth=0.56)
        self._estimator = DifferentialDrivePoseEstimator(self._kinematics, self._gyro.getRotation2d(), 0, 0,
                                                         initialPose=Pose2d(0, 0, 0))
        self.cam_to_robot = Transform3d(Translation3d(0, 0, 0), Rotation3d(0, 0, 0))

        self._field = wpilib.Field2d()
        wpilib.SmartDashboard.putData("Field", self._field)

        self.alliance = DriverStation.getAlliance()

        if hasattr(self._gyro, "gyro"):
            self.addChild("Gyro", self._gyro.gyro)

        if RobotBase.isReal():
            self.cam = PhotonCamera("photonvision")

        else: #sim
            self._motor_left_sim = SparkMaxSim(self._motor_left)
            self._motor_right_sim = SparkMaxSim(self._motor_right)
            self._system = LinearSystemId.identifyDrivetrainSystem(1.98, 0.2, 5, 0.3)
            self._drive_sim = DifferentialDrivetrainSim(self._system, 0.64, DCMotor.NEO(4), 1.5, 0.08, [
                0.001, 0.001, 0.001, 0.1, 0.1, 0.005, 0.005])

            # Cam sim
            camDiagFOV = 75.0
            maxLEDRange = 20
            camResolutionWidth = 640
            camResolutionHeight = 480
            minTargetArea = 10
            self.sim_vision = SimVisionSystem("cam", camDiagFOV, self.cam_to_robot, maxLEDRange,
                                              camResolutionWidth, camResolutionHeight, minTargetArea)
            for i in range(1, 9):
                self.sim_vision.addSimVisionTarget(SimVisionTarget(april_tag_field.getTagPose(i), 8, 8, i))
            self.cam = self.sim_vision.cam

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
        self._gyro.setSimAngle(-self._drive_sim.getHeading().degrees())
        self.sim_vision.processFrame(self._drive_sim.getPose())

    def getAngle(self):
        return self._gyro.getAngle()

    def getLeftEncoderPosition(self):
        return self._encoder_left.getPosition() - self._left_encoder_offset

    def getRightEncoderPosition(self):
        return -(self._encoder_right.getPosition() - self._right_encoder_offset)

    def getAverageEncoderPosition(self):
        return (self.getLeftEncoderPosition() + self.getRightEncoderPosition()) / 2

    def getPose(self):
        return self._estimator.getEstimatedPosition()

    def getField(self):
        return self._field

    def periodic(self):
        self._estimator.update(self._gyro.getRotation2d(), self.getLeftEncoderPosition(),
                               self.getRightEncoderPosition())

        self.latest = self.cam.getLatestResult()
        if self.latest.hasTargets():
            img_capture_time = self.latest.getTimestamp()
            cam_to_target = self.latest.getBestTarget().getBestCameraToTarget()
            target_to_cam = cam_to_target.inverse()
            target_on_field = april_tag_field.getTagPose(self.latest.getBestTarget().getFiducialId())
            camera_on_field = target_on_field.transformBy(target_to_cam)
            robot_on_field = camera_on_field.transformBy(self.cam_to_robot).toPose2d()
            self._estimator.addVisionMeasurement(robot_on_field, img_capture_time)

        self._field.setRobotPose(self._estimator.getEstimatedPosition())

        wpilib.SmartDashboard.putNumber("Left Encoder Position", self.getLeftEncoderPosition())
        wpilib.SmartDashboard.putNumber("Right Encoder Position", self.getRightEncoderPosition())
        wpilib.SmartDashboard.putNumber("Left Motor", self._motor_left.get())
        wpilib.SmartDashboard.putNumber("Right Motor", self._motor_right.get())
