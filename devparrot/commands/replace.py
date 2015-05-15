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


from devparrot.core.command import Command, Alias
from devparrot.core.constraints import Stream, Range, Default
from devparrot.core import session
import re

@Command(_section='core', ranges=Stream)
def replace(pattern, repl, ranges):
    pattern = re.compile(pattern)
    for document, rge in ranges:
        text = document.model.get(str(rge.first), str(rge.last))
        new = pattern.sub(repl, text)
        document.model.replace(str(rge.first), str(rge.last), new)

@Command(
regex = Default(help="A text (or regex) to look for"),
subst = Default(help="A substitution expression to use to replace texts found by regex"),
where = Range(default=Range.DEFAULT('all'), help="The range specifying where to do the replace")
)
def replace(regex, subst, where):
    """Replace a text by an other.

    The regex expression is used twice:

     - First, to search where the text appear in the buffer.
        This search is done using Tkinter. So the regex must be valid with tcl/tk syntax
     - Second, to found potential match groups in the regex (to be used by subst)
        This search is done using re. So the regex must also be a valid re regex.

    Subst can use references to groups defined in the regex. (See python re.sub function)
    """
    ranges = session.commands.core.search(regex, where)
    session.commands.core.replace(regex, subst, ranges)

