from typing import Literal

import rev
import wpilib

IdleMode = Literal["brake", "coast"]

__all__ = ["configureLeader", "configureFollower"]


def configureLeader(motor: rev.CANSparkMax, mode: IdleMode, inverted: bool = False):
    _handle_can_error(motor.restoreFactoryDefaults(), "restoryFactoryDefaults", motor)
    motor.setInverted(inverted)
    configureMotor(motor, mode)


def configureFollower(follower: rev.CANSparkMax, leader: rev.CANSparkMax, mode: IdleMode, inverted: bool = False):
    _handle_can_error(follower.restoreFactoryDefaults(), "restoryFactoryDefaults", follower)
    _handle_can_error(follower.setPeriodicFramePeriod(rev.CANSparkMax.PeriodicFrame.kStatus0, 1000), "set status0 rate", follower)
    _handle_can_error(follower.setPeriodicFramePeriod(rev.CANSparkMax.PeriodicFrame.kStatus1, 1000), "set status1 rate", follower)
    _handle_can_error(follower.setPeriodicFramePeriod(rev.CANSparkMax.PeriodicFrame.kStatus2, 1000), "set status2 rate", follower)
    _handle_can_error(follower.follow(leader, inverted), "follow", follower)
    _configure_motor(follower, mode)


def configureMotor(motor: rev.CANSparkMax, mode: IdleMode):
    handleCanError(motor.setIdleMode(idleModeToEnum(mode)), "setIdleMode", motor)
    handleCanError(motor.burnFlash(), "burnFlash", motor)
    handleCanError(motor.clearFaults(), "clearFaults", motor)
    wpilib.wait(0.250)


def idleModeToEnum(mode: IdleMode):
    if mode == "brake":
        return rev.CANSparkMax.IdleMode.kBrake
    elif mode == "coast":
        return rev.CANSparkMax.IdleMode.kCoast
    raise ValueError(f"mode is not 'brake' or 'coast' : {mode}")


def handleCanError(error: rev.REVLibError, function: str, motor: rev.CANSparkMax):
    if error != rev.REVLibError.kOk:
        wpilib.reportError(f"CANError on motor ID {motor.getDeviceId()} during {function} : {error}", printTrace=True)
