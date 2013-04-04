
from devparrot.core.command.baseCommand import CommandWrapper
import constraints
from constraintInstance import ConstraintInstance

class MasterCommandWrapper(object):
    def __init__(self):
        self._class = None
        self.subCommands = {}

    def set_class(self, _class):
        self._class = _class

    def add_subCommand(self, name, function):
        self.subCommands[name] = function

    def get_constraint(self, index):
        if index == 0:
            return ConstraintInstance(constraints.Keyword(self.subCommands.keys()), "subCommand")
        else:
            return self.subCommands[self.currentSubCommand].get_constraint(index-1)

    def provide_value(self, index, value):
        if index == 0:
            self.currentSubCommand = value
        else:
            self.subCommands[self.currentSubCommand].provide_value(index-1, value)

    def __call__(self, *args, **kwords):
        subCommandName = args[0]
        args = args[1:]
        return self.subCommands[subCommandName](*args, **kwords)

    def get_help(self):
        return self._class.__doc__

    def get_name(self):
        return self._class.__name__


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
                new_dct[attrName] = staticmethod(attr.functionToCall)
            else:
                new_dct[attrName] = attr
        add_command(name, wrapper)
        _class = type.__new__(cls, name, bases, new_dct)
        wrapper.set_class(_class)
        return _class


class MasterCommand(object):
    __metaclass__ = MasterCommandMeta


class SubCommand(object):
    def __init__(self, **kwords):
        streamName = None
        for name, constraint in kwords.items():
            if isinstance(constraint, constraints.Stream):
                if streamName is None:
                    streamName = name
                else:
                    raise Exception("Function can have only on stream")
        self.wrapper = CommandWrapper(kwords, streamName)

    def __call__(self, function):
        self.wrapper._set_function(function)
        return self.wrapper
