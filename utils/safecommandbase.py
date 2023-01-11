from functools import wraps

import commands2

__all__ = ["SafeCommandBase"]

fms = True
exception_threshold = 3


class CommandException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


def wrap_none(f, name):
    @wraps(f)
    def wrapped(self, *args, **kwargs):
        if wrapped._disabled:
            return
        try:
            f(self, *args, **kwargs)
            wrapped._exception_count = 0
        except Exception as e:
            if not fms:
                raise CommandException(f"Exception in command {name}.{f.__name__}()") from e
            else:
                print(f"Exception in command {name}.{f.__name__}():\n", e, sep="")
                wrapped._exception_count += 1
                if wrapped._exception_count >= exception_threshold:
                    print(f"Command method {name}.{f.__name__} has been disabled")
                    wrapped._disabled = True

    wrapped._exception_count = 0
    wrapped._disabled = False
    return wrapped


class SafeCommandMetaclass(commands2.CommandBase.__class__):
    def __new__(mcls, name, bases, dct):
        # if "execute" in dct:
        #     dct["execute"] = wrap_none(dct["execute"], name)
        cls = super().__new__(mcls, name, bases, dct)
        return cls


class SafeCommandBase(commands2.CommandBase, metaclass=SafeCommandMetaclass):
    def __init__(self):
        super().__init__()
        self.setName(self.__class__.__name__)