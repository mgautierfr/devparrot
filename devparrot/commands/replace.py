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
from devparrot.core.constraints import Stream
from devparrot.core import session

class inner:
    @staticmethod
    def replace(pattern, repl, ranges):
        import re
        model = session.get_currentDocument().model
        for start, stop in ranges:
            text = model.get(str(start), str(stop))
            new = re.sub(pattern, repl, text)
            model.replace(str(start), str(stop), new)

Command(
_section='core',
ranges=Stream()
)(inner.replace)


@Alias()
def replace(regex, subst):
    return "core.search {0!r} | core.replace {0!r} {1!r}".format(regex, subst)

