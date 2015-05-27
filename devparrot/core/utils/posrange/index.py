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


from collections import namedtuple
from devparrot.core.errors import *

all = ["Index", "Start", "End"]

class Index(namedtuple('Index', "line col")):
    def resolve(self, model):
        return self

    def __str__(self):
        global _str_cache
        if self in _str_cache:
            return _str_cache[self]
        else:
            return _str_cache.setdefault(self, "%d.%d"%(self.line, self.col))

    def __repr__(self):
        return "<Index instance pos %s>"%str(self)

Start = Index(1, 0)

class _End(Index):
    def resolve(self, model):
        return model.getend()

    def __gt__(self, other):
        return True

    def __lt__(self, other):
        return False

    def __ge__(self, other):
        return True

    def __le__(self, other):
        if isinstance(other, _End):
            return True
        return False

End   = _End(-1, -1)

_str_cache = {End:"end"}


