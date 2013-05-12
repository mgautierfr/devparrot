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

Index_ = namedtuple('Index', "line col text")

class _Index(Index_):
    def __str__(self):
        return self.text
    
    def __repr__(self):
        return "<Index instance pos %s>"%str(self)

    def __eq__(self, other):
        return self.text == other.text

    def __ne__(self, other):
        return not( self.text == other.text )

def Index(textWidget, index, indexCallNeeded = False):
    """
    Construct an index.
    @param textWidget the textWidget associated to the index. Used only to the construction of index. Not stored
    @param index the index text we want to store
    @param indexCallNeeded directly use textWidget.insert instead of try to split the text
    """

    if not indexCallNeeded:
        try:
            _split = index.split('.')
            split = (int(_split[0]), int(_split[1]))
        except ValueError:
            indexCallNeeded = True
        except IndexError:
            raise BadArgument("{} is not a valid index".format(index))

    if indexCallNeeded:
        try:
            index = textWidget.index(index)
            _split = index.split('.')
            split = (int(_split[0]), int(_split[1]))
        except TclError:
            raise BadArgument("{} is not a valid index".format(index))
    return _Index(split[0], split[1], index)

