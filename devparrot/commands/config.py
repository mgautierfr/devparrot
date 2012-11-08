from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints

class set(Command):
    configEntry = constraints.ConfigEntry()
    def run(cls, configEntry, value):
        from devparrot.core import session
        session.config.set(str(configEntry), value)
        return True
        
