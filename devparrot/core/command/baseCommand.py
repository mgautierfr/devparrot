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

import constraints
from constraintInstance import ConstraintInstance

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
        if not self.stream:
            raise StopIteration
        return self.stream.next()

    def __or__(self, streamEater):
        return streamEater(self)

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
        return Stream(self.function(*call_list))

class CommandWrapper(object):
    def __init__(self, constraints, streamName=None):
        self.constraints = constraints
        self.streamName = streamName

    def _set_function(self, function):
        from inspect import getargspec
        self.functionToCall = function
        self.argSpec = getargspec(function)
        varargConstraint = self.constraints.get(self.argSpec.varargs, None)
        if varargConstraint:
            varargConstraint.isVararg = True

    def _get_constraint(self, name):
        return self.constraints.get(name, constraints.Default())

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
                    raise TypeError
                call_kwords[constraint.name] = newVal
                del kwords[constraint.name]
            else:
                try:
                    valid, newVal = constraint.check_arg(args[0])
                    if not valid:
                        raise TypeError
                    call_kwords[constraint.name] = newVal
                    args = args[1:]
                except IndexError:
                    # no positional argument
                    try:
                        call_kwords[constraint.name] = constraint.default()
                    except constraints.noDefault:
                        if constraint.askUser:
                            call_kwords[constraint.name] = constraint.ask_user()
                        else:
                            raise TypeError

        # bind left positional arguments
        if self.argSpec.varargs and self.argSpec.varargs in self.constraints:
            constraint = ConstraintInstance(self._get_constraint(self.argSpec.varargs), self.argSpec.varargs)
            if not args:
                try:
                    call_list.append(constraint.default())
                except constraints.noDefault:
                    if constraint.askUser:
                        call_list.extend(constraint.ask_user())
                    else:
                        raise TypeError
            else:
                for arg in args:
                    valid, newVal = constraint.check_arg(arg)
                    if not valid:
                        raise TypeError
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
        try:
            call_list, call_kwords = self._get_call_args(args, kwords)
            return StreamEater(self.functionToCall, self.streamName, call_list, call_kwords, self.argSpec.args)
        except constraints.userCancel:
            pass
#        eventSystem.event("%s+"%command.__name__)(args)


class Command(object):
    def __init__(self, **kwords):
        streamName = None
        for name, constraint in kwords.items():
            if isinstance(constraint, constraints.Stream):
                if streamName is None:
                    streamName = name
                else:
                    raise Exception("Function can have only on stream")
        self.wrapper = CommandWrapper(kwords, streamName)

    def __call__(self, function, section=None):
        from devparrot.core.commandLauncher import add_command
        self.wrapper._set_function(function)
        add_command(function.__name__, self.wrapper, section)
        return function



