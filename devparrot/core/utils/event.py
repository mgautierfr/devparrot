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


from .variable import CbCaller
import collections


def hook_spawn(eventName, context):
    from devparrot.core import session
    from devparrot.core.command.bind import BindLauncher
    try:
        option = session.config.get_option("hook.%s"%eventName)
        for hookcmd in option.get(context):
            BindLauncher(hookcmd)({})
    except KeyError:
        pass

class Event(CbCaller):
    def __init__(self, eventName):
        CbCaller.__init__(self)
        self.eventName = eventName

    def __call__(self, *args, **kwords):
        if 'keys' in kwords:
            keys = kwords['keys']
            del kwords['keys']
        else:
            keys=[]
        hook_spawn(self.eventName, keys)
        self.notify(*args, **kwords)

class EventSource:
    def __init__(self):
        self.__events = dict()

    def connect(self, eventName, callback):
        self.__events.setdefault(eventName, Event(eventName)).register(callback)

    def event(self, eventName):
        return self.__events.get(eventName, Event(eventName))


def auto_bind(obj, eventSource, name_prefix="on_", wrapper=lambda caller:caller):
    for name in dir(obj):
        if name.startswith(name_prefix) and isinstance(getattr(obj, name), collections.Callable):
            eventSource.connect(name[len(name_prefix):], wrapper(getattr(obj, name)))
