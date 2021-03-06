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
from devparrot.core.constraints import Default
from devparrot.core.session import bindings

newFileNumber = 0

@Alias(
name = Default(default=lambda:None))
def new(name):
    """
    Create a new document

    Content is inserted in the document once created
    """
    global newFileNumber
    if name is None:
        name = "NewFile{}".format(newFileNumber)
        newFileNumber += 1
    return "core.buffer {0!r} new".format(name)

bindings["<Control-n>"] = "new\n"
