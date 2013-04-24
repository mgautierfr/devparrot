from devparrot.capi import Command, constraints

@Command(
    configEntry = constraints.ConfigEntry()
)
def set(configEntry, value):
    """set a config entry to value"""
    configEntry.set(value)
