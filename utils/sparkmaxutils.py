from typing import Literal

import rev
import wpilib

IdleMode = Literal["brake", "coast"]

__all__ = ["configure_leader", "configure_follower"]


def configure_leader(motor: rev.CANSparkMax, mode: IdleMode, inverted: bool = False):
    _handle_can_error(motor.restoreFactoryDefaults(), "restoreFactoryDefaults", motor)
    motor.setInverted(inverted)
    _configure_motor(motor, mode)


def configure_follower(follower: rev.CANSparkMax, leader: rev.CANSparkMax, mode: IdleMode, inverted: bool = False):
    _handle_can_error(follower.restoreFactoryDefaults(), "restoreFactoryDefaults", follower)
    _handle_can_error(follower.setPeriodicFramePeriod(rev.CANSparkMax.PeriodicFrame.kStatus0, 1000), "set status0 rate", follower)
    _handle_can_error(follower.setPeriodicFramePeriod(rev.CANSparkMax.PeriodicFrame.kStatus1, 1000), "set status1 rate", follower)
    _handle_can_error(follower.setPeriodicFramePeriod(rev.CANSparkMax.PeriodicFrame.kStatus2, 1000), "set status2 rate", follower)
    _handle_can_error(follower.follow(leader, inverted), "follow", follower)
    _configure_motor(follower, mode)


def _configure_motor(motor: rev.CANSparkMax, mode: IdleMode):
    _handle_can_error(motor.setIdleMode(_idle_mode_to_enum(mode)), "setIdleMode", motor)
    _handle_can_error(motor.burnFlash(), "burnFlash", motor)
    _handle_can_error(motor.clearFaults(), "clearFaults", motor)
    # wpilib.Timer.(0.250)


def _idle_mode_to_enum(mode: IdleMode):
    if mode == "brake":
        return rev.CANSparkMax.IdleMode.kBrake
    elif mode == "coast":
        return rev.CANSparkMax.IdleMode.kCoast
    raise ValueError(f"mode is not 'brake' or 'coast' : {mode}")


def _handle_can_error(error: rev.REVLibError, function: str, motor: rev.CANSparkMax):
    if error != rev.REVLibError.kOk:
        wpilib.reportError(f"CANError on motor ID {motor.getDeviceId()} during {function} : {error}", printTrace=True)