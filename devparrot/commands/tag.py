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


from devparrot.core.command import MasterCommand, SubCommand
from devparrot.core import session
from devparrot.core.constraints import Range

class tag(MasterCommand):
    """ Tag help stuff"""

    @SubCommand(
    where = Range(default=Range.DEFAULT('all'))
    )
    def clean(tagName, where):
        document, where = where
        document.model.tag_remove(tagName, where.first, where.end)

    @SubCommand(
    ranges = Range()
    )
    def set(tagName, *ranges):
        for doc, _range in ranges:
            doc.model.tag_add(tagName, _range.first, _range.last)



