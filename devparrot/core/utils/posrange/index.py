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

class Index(namedtuple('Index', "line col text")):
    def __new__(cls, line, col, text = None):
        if text is None:
            text = "%d.%d"%(line, col)
        return super(Index, cls).__new__(cls, line, col, text)

    def __str__(self):
        return self.text
    
    def __repr__(self):
        return "<Index instance pos %s>"%str(self)

    def __eq__(self, other):
        return other and self.text == other.text

    def __ne__(self, other):
        return not other or self.text != other.text

Start = Index(1, 0, "1.0")
End   = Index(-1, -1, "end")
