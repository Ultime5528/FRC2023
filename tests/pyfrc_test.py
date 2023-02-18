'''
    This test module imports tests that come with pyfrc, and can be used
    to test basic functionality of just about any robot.
'''
import os

from pyfrc.tests import *

def test_custom_command_names():
    for command in os.listdir("../commands"):
        if command.endswith('.py'):
            command = command[:-3]
            if command == '__init__':
                continue
            assert command in globals(), "Command %s not imported" % command