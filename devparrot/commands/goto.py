#    This file is part of DevParrot.
#
#    Author: Matthieu Gautier <matthieu.gautier@mgautier.fr>
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
#    Copyright 2011 Matthieu Gautier

from devparrot.core.command import Command
from devparrot.core import capi

@Command()
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
    if index[0] in "?/":
        model = capi.currentDocument.model
        backward = (index[0] == "?")
        if backward:
            start_search = "1.0"
            stop_search = "insert"
            get_search = -1
        else:
            start_search = "insert+1c"
            stop_search = "end"
            get_search = 0
        select = model.tag_ranges("sel")
        if select:
            if backward:
                stop_search = select[0]
            else:
                start_search = select[1]
        indices = list(model.search(index[1:], start_search, stop_search))
        if indices:
            index = indices[get_search][0]
        else:
            index = None
    if index is not None:
        capi.currentDocument.goto_index(index)

