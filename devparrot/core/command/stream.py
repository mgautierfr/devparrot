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

def DefaultStreamEater(stream):
    try:
        for _ in stream:
            pass
    except TypeError:
        pass
        

class Stream(object):
    def __init__(self, stream):
        self.stream = stream

    def __iter__(self):
        return self

    def next(self):
        if self.stream is None:
            raise StopIteration

        return self.stream.next()

class PseudoStream(Stream):
    def __init__(self):
        Stream.__init__(self, None)

class StreamEater(object):
    def __init__(self, function, streamName, args, kwords, argsorder):
        self.function = function
        self.streamName = streamName
        self.args = args
        self.kwords = kwords
        self.argsorder = argsorder

    def __call__(self, stream):
        if self.streamName:
            self.kwords[self.streamName] = stream
        call_list = [self.kwords[name] for name in self.argsorder]
        call_list.extend(self.args)
        stream_ = self.function(*call_list)
        return Stream(stream_)


