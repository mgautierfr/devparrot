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


from devparrot.core.command import Command, Alias, MasterCommand
from devparrot.core.constraints import HelpEntry

class inner:
    @staticmethod
    def help(helpEntry):
        return helpEntry.get_help()

Command(
_section='core',
helpEntry=HelpEntry()
)(inner.help)

@Alias(
helpEntry = HelpEntry(default= lambda:None)
)
def help(helpEntry):
    """The help command"""
    if helpEntry:
        helpEntryName = helpEntry.get_name()
    else:
        helpEntryName = "devparrot"
    return "core.help {0!r} | core.buffer 'help {0}'".format(helpEntryName)
