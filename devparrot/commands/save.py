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


from devparrot.core.command import Alias
from devparrot.core.constraints import File
from devparrot.core.session import bindings
from devparrot.core.errors import FileAccessError

@Alias(
fileName = File(mode=File.SAVE, default=lambda:None)
)
def save(fileName):
    """
    Save current file.

    If fileName is provided, act as "saveas" command.
    """
    from devparrot.core import session
    if fileName:
        return "core.save %current {0!r}".format(fileName)
    else:
        document = session.get_currentDocument()
        if document.has_a_path():
            return "core.save %current {0!r}".format(document.get_path())
        else:
            return "core.save %current"

@Alias(
fileName = File(mode=File.SAVE)
)
def saveas(fileName):
    """
    Save current file to fileName.

    If fileName is not provided, the user is asked for it.
    """
    return "core.save %current {0!r}".format(fileName)

bindings["<Control-s>"] = "save\n"
bindings["<Control-Shift-S>"] = "saveas\n"
