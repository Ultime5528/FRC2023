import commands2
import wpilib
import ports
from utils.safesubsystem import SafeSubsystem


class Claw(SafeSubsystem):
    def __init__(self):
        super().__init__()
        self.piston = wpilib.DoubleSolenoid(
            wpilib.PneumaticsModuleType.CTREPCM,
            ports.claw_piston_forward,
            ports.claw_piston_reverse
        )
        self.addChild("piston", self.piston)

    def open(self):
        self.piston.set(wpilib.DoubleSolenoid.Value.kForward)

    def close(self):
        self.piston.set(wpilib.DoubleSolenoid.Value.kReverse)

    def stop(self):
        self.piston.set(wpilib.DoubleSolenoid.Value.kOff)
