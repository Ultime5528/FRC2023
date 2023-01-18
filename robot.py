#!/usr/bin/env python3

import commands2
import wpilib

from subsystems.drivetrain import Drivetrain


class Robot(commands2.TimedCommandRobot):
    def robotInit(self):
        self.drivetrain = Drivetrain()

    def robotPeriodic(self) -> None:
        pass

if __name__ == "__main__":
    wpilib.run(Robot)
