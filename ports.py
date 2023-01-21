from typing import Final

"""
Respect the naming convention : "subsystem" _ "component type" _ "precision"

Put port variables into the right category: CAN - PWM - DIO

Order port numbers, ex:
    drivetrain_motor_fl: Final = 0
    drivetrain_motor_fr: Final = 1
    drivetrain_motor_rr: Final = 2
"""

# CAN
drivetrain_motor_front_right = 1
drivetrain_motor_rear_right = 2
drivetrain_motor_front_left = 3
drivetrain_motor_rear_left = 4


# PWM
...

# DIO
...
