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

import types
import constraints
from constraintInstance import ConstraintInstance


class CommandWrapper(object):
    def __init__(self, **constraints):
        self.constraints = constraints

    def _set_function(self, function):
        from inspect import getargspec
        self.function = function
        self.argSpec = getargspec(function)

    def _get_constraint(self, name):
        return self.constraints.get(name, constraints.Default())

    def _get_all_constraints(self):
        for name in  self.argSpec.args:
            yield ConstraintInstance(self._get_constraint(name), name)

    def get_constraint(self, index):
        return list(self._get_all_constraints())[index]

    def __call__(self, *args, **kwords):
        call_list = []
        call_kwords = {}
        # bind positional constraints
        for constraint in self._get_all_constraints():
            if constraint.name in kwords:
                valid, newVal = constraint.check_arg(kwords[constraint.name])
                if not valid:
                    raise TypeError
                call_list.append(newVal)
                del kwords[constraint.name]
            else:
                try:
                    valid, newVal = constraint.check_arg(args[0])
                    if not valid:
                        raise TypeError
                    call_list.append(newVal)
                    args = args[1:]
                except IndexError:
                    # no positional argument
                    if constraint.has_default:
                        call_list.append(constraint.default())
                    elif constraint.askUser:
                        call_list.append(constraint.ask_user())
                    else:
                        raise TypeError

        # bind left positional arguments
        if self.argSpec.varargs:
            constraint = ConstraintInstance(self._get_constraint(self.argSpec.varargs), self.argSpec.varargs)
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
        self.function(*call_list, **call_kwords)
#        eventSystem.event("%s+"%command.__name__)(args)


class Command(object):
    def __init__(self, **kwords):
        self.wrapper = CommandWrapper(**kwords)

    def __call__(self, function):
        self.wrapper._set_function(function)
        from devparrot.core import session
        session.add_command(function.__name__, self.wrapper)
        return function
