#    This file is part of DevParrot.
#
#    Author: Matthieu Gautier <matthieu.gautier@devparrot.org>
#
#    DevParrot is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    DevParrot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with DevParrot.  If not, see <http://www.gnu.org/licenses/>.
#
#
#    Copyright 2011-2013 Matthieu Gautier


from devparrot.capi import Command, Alias, create_section
from devparrot.capi.constraints import Command as CommandConstraint

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

Command(command=CommandConstraint()
)(inner.help, create_section("capi"))

Command()(inner.help_devparrot, create_section("capi"))

@Alias(
command = CommandConstraint(default= lambda:None)
)
def help(command):
    """The help command"""
    if command:
        commandName = command.get_name()
        line = "capi.help {0!r} | capi.buffer 'help {0}'".format(commandName)
        return line
    else:
        return "capi.help_devparrot | capi.buffer 'help devparrot'"
