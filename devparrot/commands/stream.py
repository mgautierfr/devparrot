from devparrot.core.command.baseCommand import Command
from devparrot.core.commandLauncher import create_section


def empty():
    yield ""


def null():
    raise StopIteration


Command()(empty, create_section("stream"))
Command()(null, create_section("stream"))
