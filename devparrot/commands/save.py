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


from devparrot.core.command import Alias, Command, arg_escape
from devparrot.core.constraints import File, OpenDocument
from devparrot.core.session import bindings
from devparrot.core.errors import FileAccessError

from devparrot.core import session

@Command(
document = OpenDocument(default=session.macros.current, help="document to save"),
fileName = File(mode=File.SAVE, default=lambda:None)
)
def save(document, fileName):
    """
    Save current file.

    If fileName is provided, act as "saveas" command.
    """
    if fileName:
        session.commands.core.save(document, fileName)
    else:
        if document.has_a_path():
            session.commands.core.save(document, document.get_path())
        else:
            session.commandLauncher.run_command("core.save %current")

@Alias(
fileName = File(mode=File.SAVE)
)
def saveas(fileName):
    """
    Save current file to fileName.

    If fileName is not provided, the user is asked for it.
    """
    return "core.save %current {0}".format(arg_escape(fileName))

bindings["<Control-s>"] = "save\n"
bindings["<Control-Shift-S>"] = "saveas\n"
