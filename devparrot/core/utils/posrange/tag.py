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

from .range import Range
from .index import Start, End
from devparrot.core.errors import BadArgument


class Tag:
    is_index = False
    _reduced = {"s":"sel", "selection":"sel"}
    def __init__(self, tagName):
        self.tagName = self._reduced.get(tagName, tagName)

    def resolve(self, model):
        if self.tagName == "all":
            return Range(Start , End)
        try:
            return Range(model.index("%s.first"%self.tagName) , model.index("%s.last"%self.tagName))
        except BadArgument:
            if self.tagName == "sel":
                idx = model.index("insert")
                return Range(idx, idx)
            raise

    def __eq__(self, other):
        return (self.__class__, self.tagName) == (other.__class__, other.tagName)

    def __str__(self):
        return "<TAG %s>"%self.tagName
    

