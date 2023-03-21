import random
from enum import Enum
import math
from typing import Callable, Union, Tuple, List
import commands2
import numpy
import wpilib
import ports
import numpy as np

from utils.property import autoproperty
from utils.safesubsystem import SafeSubsystem


def interpoler(t, color1, color2):
    assert 0 <= t <= 1
    return np.interp(t, color1, color2)


Color = Union[np.ndarray, Tuple[int, int, int], List[int]]


class ModeLED(Enum):
    NONE = "none"
    CONE = "cone"
    CUBE = "cube"


class LEDController(SafeSubsystem):
    brightness = autoproperty(0.2)
    # HSV: [Hue(color 0 to 180), Saturation( amount of gray 0 to 255), Value(brightness 0 to 255)
    red_rgb = np.array([255, 0, 0])
    blue_rgb = np.array([0, 0, 255])
    sky_blue_rgb = np.array([51, 51, 255])
    purple_rgb = np.array([280, 255, 255])
    violet_rgb = np.array([300, 255, 255])
    yellow_rgb = np.array([255, 255, 0])
    orange_rgb = np.array([255, 100, 0])
    black = np.array([0, 0, 0])
    white = np.array([255, 255, 255])
    beige_rgb = np.array([225, 198, 153])
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

    def setRGB(self, i: int, color: Color):
        r, g, b = color
        self.buffer[i].setRGB(r, g, b)

    def setAll(self, color_func: Callable[[int], Color]):
        a = np.arange(len(self.buffer))
        for i in np.nditer(a):
            self.setRGB(i, color_func(i))

    def pulse(self):
        pixel_value = abs(round(255 * math.cos((self.time / (18 * math.pi)))))

        if wpilib.DriverStation.getAlliance() == wpilib.DriverStation.Alliance.kRed:
            r = pixel_value
            g = 0
            b = 0
        else:
            r = 0
            g = 0
            b = pixel_value
        a = np.arange(self.led_number)
        for i in np.nditer(a):
            self.buffer[i].setRGB(r, g, b)

    def selectTeam(self):
        pixel_value = round(255 * math.cos((self.time / (18 * math.pi))))

        if pixel_value >= 0:
            r = pixel_value
            g = 0
            b = 0
        else:
            r = 0
            g = 0
            b = abs(pixel_value)

        for i in range(self.led_number):
            self.buffer[i].setRGB(r, g, b)

    def gradient(self):
        color = self.getAllianceColor()

        def getColor(i: int):
            y = 0.5 * np.sin(2 * np.pi ** 2 * (i - 2 * self.time) / 200) + 0.5
            if wpilib.DriverStation.getAlliance() == wpilib.DriverStation.Alliance.kBlue:
                color1 = interpoler(y, color, interpoler(y, color, self.purple_rgb))
                color2 = interpoler(y, color, interpoler(y, color, self.sky_blue_rgb))
                return interpoler(y, color1, color2)
            elif wpilib.DriverStation.getAlliance() == wpilib.DriverStation.Alliance.kRed:
                color3 = interpoler(y, color, interpoler(y, color, self.orange_rgb))
                color4 = interpoler(y, color, interpoler(y, color, self.beige_rgb))
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
            color = self.red_rgb
        else:  # kBlue
            color = self.blue_rgb
        return color

    def getModeColor(self):
        if self.mode == ModeLED.CUBE:
            return self.purple_rgb
        elif self.mode == ModeLED.CONE:
            return self.yellow_rgb
        else:
            return self.getAllianceColor()

    def teleop(self):
        a = 1 / (1 - math.cos(math.pi * self.white_length / self.color_period))
        k = 1 - a

        i_values = np.arange(self.led_number)
        y_values = a * np.sin(2 * math.pi / self.color_period * (i_values - self.speed * self.time)) + k
        y_values = np.maximum(y_values, 0)
        y_values = np.round(255 * y_values).astype(int)

        if wpilib.DriverStation.getAlliance() == wpilib.DriverStation.Alliance.kRed:
            for i, y in np.ndenumerate(y_values):
                self.buffer[i[0]].setRGB(255, y, y)
        else:
            for i, y in np.ndenumerate(y_values):
                self.buffer[i[0]].setRGB(y, y, 255)

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

        self.setAll(getColor)

    def setMode(self, mode: ModeLED):
        self.mode = mode

    def periodic(self) -> None:
        start_time = wpilib.getTime()

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
                if wpilib.DriverStation.isDSAttached():
                    self.pulse()
                else:
                    self.selectTeam()

        self.led_strip.setData(self.buffer)
        wpilib.SmartDashboard.putNumber("led_time", wpilib.getTime() - start_time)
