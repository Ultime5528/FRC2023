import random
from enum import Enum
import math
from typing import Callable, Union, Tuple, List
import commands2
import wpilib
import ports
import numpy as np

def interpoler(t, couleur1, couleur2):
    assert 0 <= t <= 1
    return ((1 - t) * couleur1 + t * couleur2).astype(int)


Color = Union[np.ndarray, Tuple[int, int, int], List[int]]


class ModeLED(Enum):
    NONE = "none"
    SHOOT = "shoot"
    INTAKE = "intake"


class LEDController(commands2.SubsystemBase):
    red_hsv = np.array([0, 255, 255])
    blue_hsv = np.array([120, 255, 255])
    yellow_hsv = np.array([30, 255, 255])
    orange_hsv = np.array([10, 255, 255])
    black = np.array([0, 0, 0])
    white = np.array([0, 0, 255])
    last = 0

    def __init__(self):
        super().__init__()
        self.led_strip = wpilib.AddressableLED(ports.led_strip)
        self.buffer = [wpilib.AddressableLED.LEDData() for _ in range(300)]
        self.led_strip.setLength(len(self.buffer))
        self.time = 0
        self.explosiveness = 1
        self.led_strip.start()
        self.mode = ModeLED.NONE

    def setHSV(self, i: int, color: Color):
        self.buffer[i].setHSV(*color)

    def setAll(self, color_func: Callable[[int], Color]):
        for i in range(len(self.buffer)):
            self.setHSV(i, color_func(i))

    def pulse(self, color):
        t = round(254 * abs(math.cos(self.time * 2 * math.pi / 500)**3))
        hue, saturation, _ = color
        self.setAll(lambda i: (hue, saturation, 255 - t))

    def rainbow(self):
        for i in range(len(self.buffer)):
            pixel_hue = (self.time + int(i * 180 / len(self.buffer))) % 180
            self.buffer[i].setHSV(pixel_hue, 255, i)

        self.time += 3
        self.time %= 180

    def selectTeam(self):
        pixel_value = round(510 * math.cos((1 / (12 * math.pi)) * self.time))
        if pixel_value >= 0:
            color = (125, 255, pixel_value)
        else:
            color = (0, 255, abs(pixel_value))
        self.setAll(lambda i: color)

    def ripples(self, color):
        if self.time % 10 == 0:
            def getColor(i: int):
                if random.random() <= (1 - (wpilib.DriverStation.getMatchTime() / 15)):
                    return color
                else:
                    return self.black
            self.setAll(getColor)

    def waves(self, color):
        def getColor(i: int):
            prop = 0.5 * math.cos(2 * math.pi / 20 * (self.time / 5 + i)) + 0.5
            return interpoler(prop, color, self.black)
        self.setAll(getColor)

    def halfWaves(self, color):
        def getColor(i: int):
            prop = 0.5 * math.cos((2 * math.pi / 50) * (self.time + i)) + 0.5
            if self.last - prop <= 0:
                t = prop
            else:
                t = abs(prop - 1)
            self.last = prop
            return interpoler(t, color, self.black)
        self.setAll(getColor)

    def flash(self, color, speed):
        if self.time % speed == 0:
            if self.time % (speed * 2) == 0:
                self.setAll(lambda i: color)
            else:
                self.setAll(lambda i: self.black)

    def explode(self, color):
        if self.time % 3 == 0:
            def getColor(i: int):
                y = random.random()
                if y <= self.explosiveness:
                    return interpoler(y / self.explosiveness, color, np.array([color[0], 0, 255]))
                else:
                    return self.black
            self.explosiveness -= 0.02
            self.setAll(getColor)


    def periodic(self) -> None:
        self.time += 1

        alliance = wpilib.DriverStation.getAlliance()
        if alliance == wpilib.DriverStation.Alliance.kInvalid:
            color = self.black
        elif alliance == wpilib.DriverStation.Alliance.kRed:
            color = self.red_hsv
        else:  # kBlue
            color = self.blue_hsv

        if wpilib.DriverStation.isAutonomousEnabled(): #auto
            self.ripples(color)
        elif wpilib.DriverStation.isTeleopEnabled(): #teleop
            if ModeLED.SHOOT == self.mode:
                self.halfWaves(color)
            elif ModeLED.INTAKE == self.mode:
                self.waves(color, self.intake.ballCount())
            elif wpilib.DriverStation.getMatchTime() <= 1:
                self.explode(color)
            elif wpilib.DriverStation.getMatchTime() <= 5:
                self.explosiveness = 1
                self.flash(color, 10)
            elif wpilib.DriverStation.getMatchTime() <= 15:
                self.flash(self.orange_hsv, 35)
            elif wpilib.DriverStation.getMatchTime() <= 30:
                self.flash(self.yellow_hsv, 50)
            else:
                self.waves(color, self.intake.ballCount())

        else:  # game hasn't started
            #print("disabled")
            if alliance == wpilib.DriverStation.Alliance.kInvalid:
                self.selectTeam()
            else:
                self.pulse(self.red_hsv)
        self.led_strip.setData(self.buffer)