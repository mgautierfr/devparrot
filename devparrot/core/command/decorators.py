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

from devparrot.core.command.wrappers import *
from devparrot.core.constraints import Stream

class Command:
    def __init__(self, **kwords):
        self._section = None
        self._name = None
        streamName = None
        if '_section' in kwords:
            self._section = kwords['_section']
            del kwords['_section']
        if '_name' in kwords:
            self._name = kwords['_name']
            del kwords['_name']
        for name, constraint in kwords.items():
            if isinstance(constraint, Stream):
                if streamName is None:
                    streamName = name
                else:
                    raise Exception("Function can have only one stream")
        self.wrapper = CommandWrapper(kwords, streamName)

    def __call__(self, function, section=None, functionName=None):
        from devparrot.core.commandLauncher import add_command, create_section
        from devparrot.core.help import add_helpEntry
        if section is None:
            section = self._section
        if functionName is None:
            functionName = self._name
        if functionName is None:
            functionName = function.__name__
        section = create_section(section)
        self.wrapper._set_section(section)
        self.wrapper._set_function(function, functionName)
        add_command(functionName, self.wrapper, section)
        add_helpEntry(str(self.wrapper), self.wrapper, ["commands"])
        return function


class Alias(Command):
    def __init__(self, **kwords):
        self._section = None
        self._name = None
        if '_section' in kwords:
            self._section = kwords['_section']
            del kwords['_section']
        if '_name' in kwords:
            self._name = kwords['_name']
            del kwords['_name']
        self.wrapper = AliasWrapper(kwords)

class MasterCommandMeta(type): 
    def __new__(cls, name, bases, dct):
        if name == "MasterCommand":
            return type.__new__(cls, name, bases, dct)
        from devparrot.core.commandLauncher import add_command, create_section
        from devparrot.core.help import add_helpEntry
        new_dct = {}
        wrapper = MasterCommandWrapper()
        section = None
        for attrName, attr in dct.items():
            if isinstance(attr, CommandWrapper):
                wrapper.add_subCommand(attrName, attr)
                # only keep the function in the class. wrapper is internal
                new_dct[attrName] = staticmethod(attr.functionToCall)
            elif attrName == "_section":
                section = create_section(attr)
                wrapper._set_section(section)
            else:
                new_dct[attrName] = attr
        add_command(name, wrapper, section)
        _class = type.__new__(cls, name, bases, new_dct)
        wrapper.set_class(_class)
        add_helpEntry(str(wrapper), wrapper, ["commands"])
        # we must add_helpEntry *after* the _class is set
        for attr in dct.values():
            if isinstance(attr, CommandWrapper):
                add_helpEntry(str(attr), attr, ["commands"])
        return _class


class MasterCommand(metaclass=MasterCommandMeta):
    pass


class SubCommand(Command):
    def __call__(self, function):
        functionName = self._name
        if functionName is None:
            functionName = function.__name__
        self.wrapper._set_function(function, functionName)
        # return the wrapper to be able to do some isinstance in metaclass
        return self.wrapper

class Macro(Command):
    def __init__(self, **kwords):
        self._name = None
        if '_name' in kwords:
            self._name = kwords['_name']
            del kwords['_name']
        self.wrapper = MacroWrapper(kwords)

    def __call__(self, function, functionName=None):
        from devparrot.core.commandLauncher import add_macro
        if functionName is None:
            functionName = self._name
        if functionName is None:
            functionName = function.__name__
        self.wrapper._set_function(function, functionName)
        add_macro(functionName, self.wrapper)
        return function

