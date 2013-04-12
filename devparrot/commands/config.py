from devparrot.core.command import Command
from devparrot.core import constraints

@Command(
    configEntry = constraints.ConfigEntry()
)
def set(configEntry, value):
    """set a config entry to value"""
    from devparrot.core import session
    from ast import literal_eval
    configEntry.set(value)
