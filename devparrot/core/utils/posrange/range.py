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


from devparrot.core.errors import *

class Range:
    def __init__(self, textWidget, startIndex, endIndex):
        if startIndex > endIndex:
            raise BadArgument("{} is superior to {}".format(startIndex, endIndex))
        self.textWidget = textWidget
        self.startIndex = startIndex
        self.endIndex = endIndex

    def __str__(self):
        return "%s:%s" % (str(self.startIndex), str(self.endIndex))
    
    def __repr__(self):
        return "<Range instance pos %s [%s:%s]>" % (self.textWidget, str(self.startIndex), str(self.endIndex))

    def get_content(self):
        return self.textWidget.get(str(self.startIndex), str(self.endIndex))
