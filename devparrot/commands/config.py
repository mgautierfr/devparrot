from devparrot.capi import MasterCommand, SubCommand, constraints

class config(MasterCommand):

    @SubCommand(
        configEntry = constraints.ConfigEntry()
    )
    def set(configEntry, value):
        """set a config entry to value"""
        configEntry.set(value)
