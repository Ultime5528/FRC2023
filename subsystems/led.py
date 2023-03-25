import random
from enum import Enum
import math
from typing import Callable, Union, Tuple, List
import commands2
import wpilib
import ports
import numpy as np

from utils.property import autoproperty
from utils.safesubsystem import SafeSubsystem


def interpoler(t, color1, color2):
    assert 0 <= t <= 1
    return ((1 - t) * color1 + t * color2).astype(int)


Color = Union[np.ndarray, Tuple[int, int, int], List[int]]


class ModeLED(Enum):
    NONE = "none"
    CONE = "cone"
    CUBE = "cube"


class LEDController(SafeSubsystem):
    brightness = autoproperty(0.2)
    # HSV: [Hue(color 0 to 180), Saturation( amount of gray 0 to 255), Value(brightness 0 to 255)
    red_hsv = np.array([0, 255, 255])
    red_rgb = np.array([255, 0, 0])
    blue_hsv = np.array([120, 255, 255])
    blue_rgb = np.array([0, 0, 255])
    sky_blue_hsv = np.array([120, 60, 255])
    purple_hsv = np.array([150, 255, 120])
    violet_hsv = np.array([150, 255, 240])
    yellow_hsv = np.array([29, 255, 255])
    orange_hsv = np.array([10, 255, 255])
    black = np.array([0, 0, 0])
    white = np.array([0, 0, 255])
    beige_hsv = np.array([20, 120, 255])
    led_number = 203
    speed = autoproperty(1.25)
    white_length = autoproperty(6.0)
    color_period = autoproperty(20.0)

    last = 0

    def __init__(self):
        super().__init__()
        self.led_strip = wpilib.AddressableLED(ports.led_strip)
        self.buffer = [wpilib.AddressableLED.LEDData() for _ in range(self.led_number)]
        self.led_strip.setLength(len(self.buffer))
        self.time = 0
        self.explosiveness = 0.0
        self.led_strip.start()
        self.mode = ModeLED.NONE

    def setHSV(self, i: int, color: Color):
        h, s, v = color
        # v = self.dim(v)
        self.buffer[i].setHSV(h, s, v)

    def setRGB(self, i: int, color: Color):
        r, g, b = color
        # r = self.dim(r)
        # g = self.dim(g)
        # b = self.dim(b)
        self.buffer[i].setRGB(r, g, b)

    def dim(self, x):
        return round(x * max(min(1, self.brightness), 0))

    def setAll(self, color_func: Callable[[int], Color]):
        for i in range(len(self.buffer)):
            self.setHSV(i, color_func(i))

    def setAllRGB(self, color_func: Callable[[int], Color]):
        for i in range(len(self.buffer)):
            self.setRGB(i, color_func(i))

    def pulse(self, color):
        t = abs(math.cos(self.time * 2 * math.pi / 150) ** 3)
        color = interpoler(1 - t, color, self.black)
        self.setAllRGB(lambda i: color)

    def selectTeam(self):
        pixel_value = round(255 * math.cos((self.time / (18 * math.pi))))
        if pixel_value >= 0:
            color = (pixel_value, 0, 0)
        else:
            color = (0, 0, abs(pixel_value))
        self.setAllRGB(lambda i: color)

    def gradient(self):
        color = self.getAllianceColor()

        def getColor(i: int):
            y = 0.5 * math.sin(2 * math.pi ** 2 * (i - 2 * self.time) / 200) + 0.5
            if (color == self.blue_hsv).all():
                color1 = interpoler(y, color, interpoler(y, color, self.purple_hsv))
                color2 = interpoler(y, color, interpoler(y, color, self.sky_blue_hsv))
                return interpoler(y, color1, color2)
            elif (color == self.red_hsv).all():
                color3 = interpoler(y, color, interpoler(y, color, self.orange_hsv))
                color4 = interpoler(y, color, interpoler(y, color, self.beige_hsv))
                return interpoler(y, color3, color4)
            else:
                return self.black

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

    def getAllianceColor(self):
        alliance = wpilib.DriverStation.getAlliance()
        if alliance == wpilib.DriverStation.Alliance.kInvalid:
            color = self.black
        elif alliance == wpilib.DriverStation.Alliance.kRed:
            color = self.red_hsv
        else:  # kBlue
            color = self.blue_hsv
        return color

    def getModeColor(self):
        if self.mode == ModeLED.CUBE:
            return self.purple_hsv
        elif self.mode == ModeLED.CONE:
            return self.yellow_hsv
        else:
            return self.getAllianceColor()

    def teleop(self):
        a = 1 / (1 - math.cos(math.pi * self.white_length / self.color_period))
        k = 1 - a
        def getColor(i: int):
            y = a * math.sin(2 * math.pi / self.color_period * (i - self.speed * self.time)) + k
            y = max(y, 0)
            return interpoler(y, self.getModeColor(), self.white)

        return self.setAll(getColor)

    def e_stopped(self):
        interval = 10
        flash_time = 20
        state = round(self.time / flash_time) % 2

        def getColor(i: int):
            is_color = state - round(i / interval) % 2
            if is_color:
                return self.red_rgb
            else:
                return self.black

        self.setAllRGB(getColor)

    def setMode(self, mode: ModeLED):
        self.mode = mode

    def periodic(self) -> None:
        self.time += 1
        if wpilib.DriverStation.isEStopped():
            self.e_stopped()
        elif self.explosiveness > 0.0:
            self.explode(self.getAllianceColor())
        else:
            if wpilib.DriverStation.isAutonomousEnabled():  # auto
                self.gradient()
            elif wpilib.DriverStation.isTeleopEnabled():  # teleop
                if wpilib.DriverStation.getMatchTime() == -1.0 or wpilib.DriverStation.getMatchTime() > 30:
                    self.teleop()
                elif wpilib.DriverStation.getMatchTime() > 25:
                    self.flash(self.getAllianceColor(), 10)
                elif wpilib.DriverStation.getMatchTime() > 1:
                    self.halfWaves(self.getModeColor())
                else:
                    self.explosiveness = 1
                    self.explode(self.getAllianceColor())
            else:  # game hasn't started
                if wpilib.DriverStation.isDSAttached() and wpilib.DriverStation.getAlliance() == wpilib.DriverStation.Alliance.kRed:
                    self.pulse(self.red_rgb)
                elif wpilib.DriverStation.isDSAttached() and wpilib.DriverStation.getAlliance() == wpilib.DriverStation.Alliance.kBlue:
                    self.pulse(self.blue_rgb)
                else:
                    self.selectTeam()

        self.led_strip.setData(self.buffer)
