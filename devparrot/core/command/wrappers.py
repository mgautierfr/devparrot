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

from devparrot.core.constraints import ConstraintInstance, Default, Keyword
from devparrot.core.command.stream import StreamEater
from devparrot.core.errors import *

class CommandWrapper(object):
    def __init__(self, constraints, streamName=None):
        self.constraints = constraints
        self.streamName = streamName
        self.section = None

    def _set_section(self, section):
        self.section = section

    def _set_function(self, function):
        from inspect import getargspec
        self.functionToCall = function
        self.argSpec = getargspec(function)
        varargConstraint = self.constraints.get(self.argSpec.varargs, None)
        if varargConstraint:
            varargConstraint.isVararg = True

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

    def provide_value(self, index, value):
        pass

    def _get_call_args(self, args, kwords):
        call_list = []
        call_kwords = {}
        # bind positional constraints
        for constraint in self._get_all_constraints():
            if constraint.name in kwords:
                valid, newVal = constraint.check_arg(kwords[constraint.name])
                if not valid:
                    raise InvalidArgument("%s is not valid for constraint %s", kwords[constraint.name], constraint)
                call_kwords[constraint.name] = newVal
                del kwords[constraint.name]
            else:
                try:
                    valid, newVal = constraint.check_arg(args[0])
                    if not valid:
                        raise InvalidArgument("%s is not valid for constraint %s", args[0], constraint)
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
                            raise InvalidArgument("missing argument for constraint %s", constraint)

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
                        raise InvalidArgument("missing argument for constraint %s", constraint)
            else:
                for arg in args:
                    valid, newVal = constraint.check_arg(arg)
                    if not valid:
                        raise InvalidArgument("%s is not valid for constraint %s", arg, constraint)
                    call_list.append(newVal)
        else:
            # this will make the call fail, but user will have some info
            call_list.extend(args)

        # bind left keyword arguments
        call_kwords.update(kwords)
#TODO reactive the event stuff
#        eventSystem.event("%s-"%command.__name__)(args)

        return call_list, call_kwords

    def __call__(self, *args, **kwords):
        call_list, call_kwords = self._get_call_args(args, kwords)
        return StreamEater(self.functionToCall, self.streamName, call_list, call_kwords, self.argSpec.args)
#        eventSystem.event("%s+"%command.__name__)(args)

    def get_help(self):
        helps = []
        helps.append("%s command:"%self.get_name())
        helps.append("="*len(helps[-1]))
        helps.append("")

        helps.append(self.functionToCall.__doc__ or "no description...")
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
            return "%s.%s"%(self.section.get_name(), self.functionToCall.__name__)
        return self.functionToCall.__name__

class AliasWrapper(CommandWrapper):
    def __init__(self, constraints):
        CommandWrapper.__init__(self, constraints, None)

    def __call__(self, *args, **kwords):
        call_list, call_kwords = self._get_call_args(args, kwords)
        return self.functionToCall(*call_list, **call_kwords)

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
            return ConstraintInstance(Keyword(self.subCommands.keys()), "subCommand")
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

