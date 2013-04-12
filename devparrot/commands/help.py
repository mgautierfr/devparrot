
from devparrot.core.command import Command, Alias
from devparrot.core.commandLauncher import create_section
from devparrot.core import constraints

class inner:
    @staticmethod
    def help(command):
        helpText = command.get_help()
        for line in helpText.split('\n'):
            yield "%s\n"%line

Command(command=constraints.Command()
)(inner.help, create_section("capi"))

@Alias(
command = constraints.Command(default= lambda:None)
)
def help(command):
    """The help command"""
    commandName = command.get_name() if command else "help"
    line = "capi.help %(commandName)s | capi.buffer 'help %(commandName)s"%{'commandName':commandName}
    return line
