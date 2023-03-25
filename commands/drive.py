import commands2.button
import wpilib
from wpimath.filter import LinearFilter

from subsystems.drivetrain import Drivetrain
from utils.property import autoproperty
from utils.safecommand import SafeCommand


class Drive(SafeCommand):
    smoothing_window = autoproperty(1)
    interpolation_curve = autoproperty(0.6)
    deadzone_x = autoproperty(0.1)
    deadzone_y = autoproperty(0.1)

    def __init__(self, drivetrain: Drivetrain, stick: wpilib.Joystick):
        super().__init__()
        self.addRequirements(drivetrain)
        self.stick = stick
        self.drivetrain = drivetrain

    def initialize(self) -> None:
        self.forward_filter = LinearFilter.movingAverage(int(self.smoothing_window))
        self.turn_filter = LinearFilter.movingAverage(int(self.smoothing_window))

    def execute(self):
        if isinstance(self.stick, commands2.button.CommandXboxController):
            forward = self.interpolate(self.stick.getLeftY()) * -1
            turn = self.interpolate(self.stick.getLeftX()) * -1
        elif isinstance(self.stick, commands2.button.CommandJoystick):
            forward = self.interpolate(self.stick.getY()) * -1
            turn = self.interpolate(self.stick.getX()) * -1

        self.drivetrain.arcadeDrive(self.forward_filter.calculate(forward), self.turn_filter.calculate(turn))

    def end(self, interrupted: bool) -> None:
        self.drivetrain.arcadeDrive(0.0, 0.0)

    def interpolate(self, value: float):
        curve = self.interpolation_curve
        deadzone_x = self.deadzone_x
        deadzone_y = self.deadzone_y

        if value >= deadzone_x:
            return deadzone_y + (1 - deadzone_y) * (curve * value ** 3 + (1 - curve) * value)
        elif value <= -deadzone_x:
            return -deadzone_y + (1 - deadzone_y) * (curve * value ** 3 + (1 - curve) * value)
        else:
            return 0.0
