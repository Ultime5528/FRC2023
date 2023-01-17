import wpilib
from commands2 import CommandBase
from wpimath.filter import LinearFilter
import properties
from subsystems.drivetrain import Drivetrain
from utils.safecommandbase import SafeCommandBase


def interpolate(value: float):
    curve = properties.values.drive_interpolation_curve
    deadzone_x = properties.values.drive_deadzone_x
    deadzone_y = properties.values.drive_deadzone_y

    if value >= deadzone_x:
        return deadzone_y + (1 - deadzone_y) * (curve * value**3 + (1 - curve) * value)
    elif value <= -deadzone_x:
       return -deadzone_y + (1 - deadzone_y) * (curve * value**3 + (1 - curve) * value)
    else:
        return 0.0  # interpolate(deadzone_x) / deadzone_x * value;


class Drive(SafeCommandBase):
    def __init__(self, drivetrain: Drivetrain, stick: wpilib.Joystick):
        super().__init__()
        self.stick = stick
        self.drivetrain = drivetrain

    def initialize(self) -> None:
        self.forward_filter = LinearFilter.movingAverage(int(properties.values.drive_smoothing_window))
        self.turn_filter = LinearFilter.movingAverage(int(properties.values.drive_smoothing_window))

    def execute(self):
        forward = interpolate(self.stick.getY()) * -1
        turn = interpolate(self.stick.getX()) * -1

        self.drivetrain.arcadeDrive(self.forward_filter.calculate(forward), self.turn_filter.calculate(turn))
