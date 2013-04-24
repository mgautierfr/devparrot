
from devparrot.core.command import Command, Alias
from devparrot.core.commandLauncher import create_section
from devparrot.core import constraints

class inner:
    @staticmethod
    def help(command):
        helpText = command.get_help()
        for line in helpText.split('\n'):
            yield "{}\n".format(line)

    @staticmethod
    def help_devparrot():
        from devparrot.core import session
        from devparrot.core.command.section import Section
        commands = [key for key, command in session.commands.items() if not isinstance(command, Section)]
        helps = []
        yield "Devparrot help\n"
        yield "==============\n"
        yield "\n"
        
        yield "commands :\n"
        yield "----------\n"
        yield "\n"
        for command in commands:
            yield " - {}\n".format(command)

Command(command=constraints.Command()
)(inner.help, create_section("capi"))

Command()(inner.help_devparrot, create_section("capi"))

@Alias(
command = constraints.Command(default= lambda:None)
)
def help(command):
    """The help command"""
    if command:
        commandName = command.get_name()
        line = "capi.help {0!r} | capi.buffer 'help {0}'".format(commandName)
        return line
    else:
        return "capi.help_devparrot | capi.buffer 'help devparrot'"
