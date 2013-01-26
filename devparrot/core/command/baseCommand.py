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
        self.function = function

    def _get_constraint(self, name):
        return self.constraints.get(name, constraints.Default())

    def _get_all_constraints(self, func_code):
        for name in func_code.co_varnames[:func_code.co_argcount]:
            yield ConstraintInstance(self._get_constraint(name), name)

    def get_constraint(self, index):
        return list(self._get_all_constraints(self.function.func_code))[index]

    def __call__(self, *args, **kwords):
        current_index = 0
        call_kwords = {}
        for constraint in self._get_all_constraints(self.function.func_code):
            if constraint.name in kwords:
                if not constraint.check_arg(kwords[constraint.name]):
                    return
                call_kwords[constraint.name] = kwords[constraint.name]
            else:
                try:
                    if not constraint.check_arg(args[current_index]):
                        return
                    call_kwords[constraint.name] = args[current_index]
                    current_index += 1
                except IndexError:
                    if constraint.has_default:
                        call_kwords[constraint.name] = constraint.default()
                    elif constraint.askUser:
                        call_kwords[constraint.name] = constraint.ask_user()
                    else:
                        return
#TODO reactive the event stuff
#        eventSystem.event("%s-"%command.__name__)(args)
        self.function(**call_kwords)
#        eventSystem.event("%s+"%command.__name__)(args)


class Command(object):
    def __init__(self, **kwords):
        self.wrapper = CommandWrapper(**kwords)

    def __call__(self, function):
        self.wrapper._set_function(function)
        from devparrot.core import session
        session.add_command(function.__name__, self.wrapper)
        return function
