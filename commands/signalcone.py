import math

import wpilib
from subsystems.led import LEDController
from utils.property import autoproperty
from utils.safecommand import SafeCommand


class SignalCone(SafeCommand):
    duration = autoproperty(2.0)
    def __init__(self, led_controller: LEDController):
        super().__init__()
        self.led_controller = led_controller
        self.timer = wpilib.Timer()


    def initialize(self) -> None:
        self.timer.reset()
        self.timer.start()

    def execute(self) -> None:
        self.led_controller.setMode("CONE")

    def isFinished(self) -> bool:
        return self.timer.get() >= self.duration

    def end(self, interrupted: bool) -> None:
        self.led_controller.setMode("NONE")

