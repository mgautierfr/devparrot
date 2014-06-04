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

from devparrot.core import session
from devparrot.core.errors import ContextError

def DefaultStreamEater(stream):
    try:
        for _ in stream:
            pass
    except TypeError:
        pass
        

class Stream(object):
    def __init__(self, functionName, stream):
        self.functionName = functionName
        self.stream = stream

    def __iter__(self):
        return self

    def next(self):
        try:
            if self.stream is None:
                raise StopIteration

            return self.stream.next()
        except StopIteration:
            if self.functionName is not None:
                session.eventSystem.event("{}+".format(self.functionName))()
            raise StopIteration

class PseudoStream(Stream):
    def __init__(self):
        Stream.__init__(self, None, None)

class StreamEater(object):
    def __init__(self, function, functionName, streamName, args, kwords, argsorder):
        self.function = function
        self.functionName = functionName
        self.streamName = streamName
        self.args = args
        self.kwords = kwords
        self.argsorder = argsorder

    def __call__(self, stream):
        if self.streamName:
            self.kwords[self.streamName] = stream
        call_list = [self.kwords[name] for name in self.argsorder]
        call_list.extend(self.args)
        session.eventSystem.event("{}-".format(self.functionName))()
        try:
            stream_ = self.function(*call_list)
        except Exception as err:
            raise ContextError("Error in %s (%s) : %s"%(self.functionName, err.__class__.__name__,str(err)))
        session.eventSystem.event("{}=".format(self.functionName))()
        return Stream(self.functionName, stream_)


