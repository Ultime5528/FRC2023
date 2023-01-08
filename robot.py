#!/usr/bin/env python3

import commands2
import wpilib


class Robot(commands2.TimedCommandRobot):
    def robotInit(self):
        pass


if __name__ == "__main__":
    wpilib.run(Robot)
