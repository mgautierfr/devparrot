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


from devparrot.core.command.wrappers import *
from devparrot.core.constraints import Stream

class Command(object):
    def __init__(self, **kwords):
        streamName = None
        for name, constraint in kwords.items():
            if isinstance(constraint, Stream):
                if streamName is None:
                    streamName = name
                else:
                    raise Exception("Function can have only one stream")
        self.wrapper = CommandWrapper(kwords, streamName)

    def __call__(self, function, section=None):
        from devparrot.core.commandLauncher import add_command
        self.wrapper._set_section(section)
        self.wrapper._set_function(function)
        add_command(function.__name__, self.wrapper, section)
        return function


class Alias(Command):
    def __init__(self, **kwords):
        self.wrapper = AliasWrapper(kwords)

class MasterCommandMeta(type): 
    def __new__(cls, name, bases, dct):
        if name == "MasterCommand":
            return type.__new__(cls, name, bases, dct)
        from devparrot.core.commandLauncher import add_command
        new_dct = {}
        wrapper = MasterCommandWrapper()
        for attrName, attr in dct.items():
            if isinstance(attr, CommandWrapper):
                wrapper.add_subCommand(attrName, attr)
                # only keep the function in the class. wrapper is internal
                new_dct[attrName] = staticmethod(attr.functionToCall)
            else:
                new_dct[attrName] = attr
        add_command(name, wrapper)
        _class = type.__new__(cls, name, bases, new_dct)
        wrapper.set_class(_class)
        return _class


class MasterCommand(object):
    __metaclass__ = MasterCommandMeta


class SubCommand(Command):
    def __call__(self, function):
        self.wrapper._set_function(function)
        # return the wrapper to be able to do some isinstance in metaclass
        return self.wrapper
