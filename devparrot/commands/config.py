from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints

@Command(
    configEntry = constraints.ConfigEntry()
)
def set(configEntry, value):
    from devparrot.core import session
    from ast import literal_eval
    configEntry.set(literal_eval(value))
    return True
