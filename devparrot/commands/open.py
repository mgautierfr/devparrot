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


import os.path
from devparrot.core.command import Command
from devparrot.core.constraints import File
from devparrot.core import session

@Command(
files = File(mode=(File.OPEN, File.NEW), help="a list of file to open")
)
def open(*files):
    """
    Open a existing or new file
    """
    for fileToOpen in files:
        lineToGo = 1
        if not os.path.exists(fileToOpen):
            parts = fileToOpen.split(':')
            if len(parts) == 2:
                fileToOpen = parts[0]
                try :
                    lineToGo = int(parts[1])
                except ValueError:
                    pass
        session.commands.core.open(fileToOpen)
        session.commandLauncher.run_command('core.see %d'%lineToGo)

session.bindings["<Control-o>"] = "open\n"
