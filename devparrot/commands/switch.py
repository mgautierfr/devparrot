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


from devparrot.capi import Command, set_currentDocument
from devparrot.capi.constraints import OpenDocument
from devparrot.core.session import bindings

@Command(
document = OpenDocument()
)
def switch(document):
    """set focus to document"""
    set_currentDocument(document)


bindings["<Alt-Right>"] = "switch $right\n"
bindings["<Alt-Left>"] = "switch $left\n"
bindings["<Alt-Up>"] = "switch $top\n"
bindings["<Alt-Down>"] = "switch $bottom\n"
bindings["<Alt-Prior>"] = "switch $previous\n"
bindings["<Alt-Next>"] = "switch $next\n"
