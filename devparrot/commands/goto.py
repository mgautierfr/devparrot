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


from devparrot.capi import Command, set_currentDocument, constraints
from devparrot.core import errors

@Command(
index = constraints.Index()
)
def goto(index):
    """
    goto to index
    set insert mare to index and see it.

    index can be:
        - a string that tk will understand :
         . "lineNumber.charNumber" (line start from 1, char start from 0"
         . a mark name
        - a ex search syntax :
         . [?/]regex
    """
    document, index = index
    set_currentDocument(document)
    document.goto_index(index)

