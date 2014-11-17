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


from devparrot.core.constraints import ConstraintInstance, Default, Keyword
from devparrot.core.command.stream import StreamEater
from devparrot.core.errors import *
import inspect

class CommandWrapper(object):
    def __init__(self, constraints, streamName=None):
        self.constraints = constraints
        self.streamName = streamName
        self.section = None
        self.masterCommand = None

    def _set_section(self, section):
        self.section = section

    def _set_masterCommand(self, masterCommand):
        self.masterCommand = masterCommand

    def _set_function(self, function, commandName):
        from inspect import getargspec
        self.functionToCall = function
        if self.section is not None:
            self.commandName = "{}.{}".format(self.section.name, commandName)
        else:
            self.commandName = commandName
        self.argSpec = getargspec(function)
        varargConstraint = self.constraints.get(self.argSpec.varargs, None)
        if varargConstraint:
            varargConstraint.isVararg = True

    def _set_commandName(self, name):
        self.commandName = name

    def _get_constraint(self, name):
        return self.constraints.get(name, Default())

    def _get_all_constraints(self):
        for name in  self.argSpec.args:
            if name != self.streamName:
                yield ConstraintInstance(self._get_constraint(name), name)

    def get_constraint(self, index):
        try:
            return list(self._get_all_constraints())[index]
        except IndexError:
            if self.argSpec.varargs:
                return ConstraintInstance(self._get_constraint(self.argSpec.varargs), self.argSpec.varargs)
            raise

    def provide_value(self, index, token):
        pass

    def _get_call_args(self, args, kwords):
        call_list = []
        call_kwords = {}
        # bind positional constraints
        for constraint in self._get_all_constraints():
            if constraint.name in kwords:
                valid, newVal = constraint.check_arg(kwords[constraint.name])
                if not valid:
                    raise InvalidArgument("Command {} : {} is not valid for constraint {}".format(self.commandName, kwords[constraint.name], constraint))
                call_kwords[constraint.name] = newVal
                del kwords[constraint.name]
            else:
                try:
                    valid, newVal = constraint.check_arg(args[0])
                    if not valid:
                        raise InvalidArgument("Command {} : {} is not valid for constraint {}".format(self.commandName, args[0], constraint))
                    call_kwords[constraint.name] = newVal
                    args = args[1:]
                except IndexError:
                    # no positional argument
                    try:
                        call_kwords[constraint.name] = constraint.default()
                    except NoDefault:
                        if constraint.askUser:
                            call_kwords[constraint.name] = constraint.ask_user()
                        else:
                            raise InvalidArgument("Command {} : missing argument for constraint {}".format(self.commandName, constraint))

        # bind left positional arguments
        if self.argSpec.varargs and self.argSpec.varargs in self.constraints:
            constraint = ConstraintInstance(self._get_constraint(self.argSpec.varargs), self.argSpec.varargs)
            if not args:
                try:
                    call_list.append(constraint.default())
                except NoDefault:
                    if constraint.askUser:
                        call_list.extend(constraint.ask_user())
                    else:
                        raise InvalidArgument("missing argument for constraint {}".format(constraint))
            else:
                for arg in args:
                    valid, newVal = constraint.check_arg(arg)
                    if not valid:
                        raise InvalidArgument("{} is not valid for constraint {}".format(arg, constraint))
                    call_list.append(newVal)
        else:
            # this will make the call fail, but user will have some info
            call_list.extend(args)

        # bind left keyword arguments
        call_kwords.update(kwords)


        return call_list, call_kwords

    def resolve(self, *args, **kwords):
        call_list, call_kwords = self._get_call_args(args, kwords)
        return StreamEater(self.functionToCall, self.streamName, call_list, call_kwords, self.argSpec.args)

    def __call__(self, *args, **kwords):
        return self.functionToCall(*args, **kwords)

    def get_help(self):
        helps = []
        helps.append("%s command:"%self.get_name())
        helps.append("="*len(helps[-1]))
        helps.append("")

        helps.append(inspect.getdoc(self.functionToCall) or "no description...")
        helps.append("\n")
        
        helps.append("Arguments:")
        helps.append("-"*len(helps[-1]))
        helps.append("")
        for constraint in self._get_all_constraints():
            helps.append(constraint.get_help())

        if self.argSpec.varargs and self.argSpec.varargs in self.constraints:
            constraint = ConstraintInstance(self._get_constraint(self.argSpec.varargs), self.argSpec.varargs)
            helps.append(constraint.get_help())

        helps.append("")
        helps.append(" - stream : %s"%self.streamName)
        if self.streamName:
            constraint = self._get_constraint(self.streamName)
            helps.append(constraint.get_help())

        return "\n".join(helps)

    def get_name(self):
        if self.section:
            name =  "%s.%s"%(self.section.get_name(), self.functionToCall.__name__)
        else:
            name =  self.functionToCall.__name__
        if self.masterCommand:
            return "%s %s"%(self.masterCommand.get_name(), name)
        return name

class AliasWrapper(CommandWrapper):
    def __init__(self, constraints):
        CommandWrapper.__init__(self, constraints, None)

    def resolve(self, *args, **kwords):
        call_list, call_kwords = self._get_call_args(args, kwords)
        return self.functionToCall(*call_list, **call_kwords)

class MasterCommandWrapper(object):
    def __init__(self):
        self._class = None
        self.subCommands = {}
        self.section = None

    def _set_section(self, section):
        self.section = section

    def set_class(self, _class):
        self._class = _class

    def add_subCommand(self, name, function):
        self.subCommands[name] = function
        function._set_masterCommand(self)

    def get_constraint(self, index):
        if index == 0:
            return ConstraintInstance(Keyword(self.subCommands.keys()), "subCommand")
        else:
            return self.subCommands[self.currentSubCommand].get_constraint(index-1)

    def provide_value(self, index, token):
        if index == 0:
            self.currentSubCommand = token.values
        else:
            self.subCommands[self.currentSubCommand].provide_value(index-1, token)

    def resolve(self, *args, **kwords):
        subCommandName = args[0]
        args = args[1:]
        return self.subCommands[subCommandName].resolve(*args, **kwords)

    def get_help(self):
        helps = []
        helps.append("%s master command:"%self.get_name())
        helps.append("="*len(helps[-1]))
        helps.append("")

        helps.append(inspect.getdoc(self._class) or "no description...")
        helps.append("\n")

        helps.append("SubCommands:")
        helps.append("-"*len(helps[-1]))
        helps.append("")
        for subcommand in self.subCommands:
            helps.append(" - %s"%subcommand)

        return "\n".join(helps)

    def get_name(self):
        if self.section:
            return "%s.%s"%(self.section.get_name(), self._class.__name__)
        return self._class.__name__

    def __getitem__(self, name):
        return self.subCommands[name]

class MacroWrapper(CommandWrapper):
    def __init__(self, constraints):
        CommandWrapper.__init__(self, constraints, None)

    def resolve(self, *args, **kwords):
        call_list, call_kwords = self._get_call_args(args, kwords)
        return self.functionToCall(*call_list, **call_kwords)

class MacroDict(MacroWrapper):
    def __init__(self, kwords):
        MacroWrapper.__init__(self, {})
        self.kwords = kwords

    def resolve(self, *args, **kwords):
        return self.kwords[args[0]]


class MacroResult(object):
    def __init__(self, result):
        self.result = result

    def __str__(self):
        return "<MacroResult %s>"%self.result

    def __call__(self):
        return self.result
