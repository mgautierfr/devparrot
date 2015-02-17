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
        

class Stream:
    def __init__(self, stream):
        self.stream = stream
        self._iter = iter(stream) if stream else None

    def __iter__(self):
        return self

    def __next__(self):
        if self.stream is None:
            raise StopIteration

        return next(self._iter)

class PseudoStream(Stream):
    def __init__(self):
        Stream.__init__(self, None)

class StreamEater:
    def __init__(self, function, streamName, args, kwords, signature):
        self.function = function
        self.streamName = streamName
        self.args = args
        self.kwords = kwords
        self.signature = signature

    def __call__(self, stream):
        if self.streamName:
            self.kwords[self.streamName] = stream
        bound = self.signature.bind(*self.args, **self.kwords)
        stream_ = self.function(*bound.args, **bound.kwargs)
        return Stream(stream_)


