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
from devparrot.core.constraints import Stream, Range
from devparrot.core import session
import re

class inner:
    @staticmethod
    def replace(pattern, repl, ranges):
        print('pattern', pattern)
        pattern = re.compile(pattern)
        for document, rge in ranges:
            text = document.model.get(str(rge.first), str(rge.last))
            print('text', text)
            new = pattern.sub(repl, text)
            print('new', new)
            document.model.replace(str(rge.first), str(rge.last), new)

Command(
_section='core',
ranges=Stream()
)(inner.replace)


@Command(
where = Range(default=Range.DEFAULT('all'))
)
def replace(regex, subst, where):
    ranges = session.commands.core.search(regex, where)
    session.commands.core.replace(regex, subst, ranges)

