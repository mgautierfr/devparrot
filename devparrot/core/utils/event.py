#    This file is part of DevParrot.
#
#    Author: Matthieu Gautier <matthieu.gautier@mgautier.fr>
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
#    Copyright 2011 Matthieu Gautier

from variable import CbCaller

class Event(CbCaller):
    def __call__(self, *args, **kwords):
        self.notify(*args, **kwords)


class EventSource(object):
    def __init__(self):
        self.__events = dict()

    def connect(self, eventName, callback):
        self.__events.setdefault(eventName, Event()).register(callback)

    def event(self, eventName):
        return self.__events.get(eventName, Event())


