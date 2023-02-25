from subsystems.drivetrain import Drivetrain
from utils.property import autoproperty
from utils.safecommand import SafeCommand
from utils.trapezoidalmotion import TrapezoidalMotion


class Turn(SafeCommand):
    min_speed = autoproperty(0.15)
    accel = autoproperty(0.002)

    def __init__(self, drivetrain: Drivetrain, angle: float, speed: float):
        """
        Parameters
        ----------
        drivetrain
        angle: Positif = antihoraire
        speed: SPEEED
        """

        super().__init__()
        self.motion = TrapezoidalMotion(
            start_position=0,
            end_position=angle,
            start_speed=speed,
            min_speed=self.min_speed,
            max_speed=speed,
            accel=self.accel
        )
        self.drivetrain = drivetrain
        self.addRequirements(drivetrain)
        self.angle = angle
        self.cumul = 0
        self.previous_rotation = self.drivetrain.getRotation()

    def initialize(self) -> None:
        self.cumul = 0
        self.previous_rotation = self.drivetrain.getRotation()

    def execute(self):
        current_rotation = self.drivetrain.getRotation()
        moved_rotation = current_rotation - self.previous_rotation
        self.cumul += moved_rotation.degrees()
        self.motion.setPosition(self.cumul)
        self.drivetrain.arcadeDrive(0, self.motion.getSpeed())
        self.previous_rotation = current_rotation

    def isFinished(self) -> bool:
        return self.motion.isFinished()

    def end(self, interrupted: bool) -> None:
        pass
