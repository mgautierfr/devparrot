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


from devparrot.capi import Command, get_currentDocument, save_document
from devparrot.capi import constraints
from devparrot.core.session import bindings
from devparrot.core.errors import NoDefault, FileAccessError

def _get_default():
    if get_currentDocument() is None:
        raise NoDefault()
    if get_currentDocument().has_a_path():
        return get_currentDocument().get_path()
    raise NoDefault()
        
@Command(
fileName = constraints.File(mode=constraints.File.SAVE, default=_get_default)
)
def save(fileName):
    """
    Save current file.

    If fileName is provided, act as "saveas" command.
    """
    try:
        save_document(get_currentDocument(), fileName)
    except IOError:
        raise FileAccessError(fileName)

@Command(
fileName = constraints.File(mode=constraints.File.SAVE)
)
def saveas(fileName):
    """
    Save current file to fileName.

    If fileName is not provided, the user is asked for it.
    """
    try:
        save_document(get_currentDocument(), fileName)
    except IOError:
        raise FileAccessError(fileName)

bindings["<Control-s>"] = "save\n"
bindings["<Control-Shift-S>"] = "saveas\n"
