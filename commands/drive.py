import wpilib
from commands2 import CommandBase
from wpimath.filter import LinearFilter
import properties
from subsystems.drivetrain import Drivetrain


def interpolate(value: float):
    curve = properties.values.drive_interpolation_curve
    deadzoneX = properties.values.drive_deadzone_x
    deadzoneY = properties.values.drive_deadzone_y

    if value >= deadzoneX:
        return deadzoneY + (1 - deadzoneY) * (curve * value**3 + (1 - curve) * value)
    elif value <= -deadzoneX:
       return -deadzoneY + (1 - deadzoneY) * (curve * value**3 + (1 - curve) * value)
    else:
        return 0.0  # interpolate(deadzoneX) / deadzoneX * value;


class Drive(CommandBase):
    def __init__(self, drivetrain: Drivetrain, stick: wpilib.Joystick):
        super().__init__()
        self.stick = stick
        self.drivetrain = drivetrain
        self.addRequirements(drivetrain)
        self.setName("Drive")

    def initialize(self) -> None:
        self.forward_filter = LinearFilter.movingAverage(int(properties.values.drive_smoothing_window))
        self.turn_filter = LinearFilter.movingAverage(int(properties.values.drive_smoothing_window))

    def execute(self):
        forward = interpolate(self.stick.getY()) * -1
        turn = interpolate(self.stick.getX()) * -1

        self.drivetrain.arcadeDrive(self.forward_filter.calculate(forward), self.turn_filter.calculate(turn))
