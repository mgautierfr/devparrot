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
import pyparsing

class MetaAction(type):
	def __new__(cls, name, bases, dct):
		#dct['accelerators'] = list()
		for (key, value) in dct.items():
			if isinstance(value, types.FunctionType):
				cm = classmethod(value)
				dct[key] = cm
		return type.__new__(cls, name, bases, dct)

	def __init__(cls, name, bases, dct):
		super(MetaAction, cls).__init__(name, bases, dct)
		if name != "Action":
			from devparrot.core import commandLauncher
			commandLauncher.add_alias(name, cls, 0)
		

class Action:
	__metaclass__ = MetaAction

	def add_alias(cls, newName, oldName = None, prio=None):
		from devparrot.core import commandLauncher
		oldName = oldName or cls.__name__
		if prio is None:
			commandLauncher.add_alias(newName, oldName)
		else:
			commandLauncher.add_alias(newName, oldName, prio)

	def add_expender(cls, expender):
		from devparrot.core import commandLauncher
		commandLauncher.add_expender(expender)

	def pre_check(cls, cmdText):
		return True
	
	def get_tokenParser(cls):
		return constraints.TokenParser(cls.get_allConstraints(),askUser=True)
	
	def get_argNumber(cls):
		return cls.run.func_code.co_argcount-2
		
	def get_argName(cls, index):
		return cls.run.func_code.co_varnames[index+2]
	
	def get_argNames(cls):
		return cls.run.func_code.co_varnames[2:cls.run.func_code.co_argcount]

	def get_constraint(cls, name):
		return cls.__dict__.get(name, constraints.Default())
		
	def get_allConstraints(cls):
		for name in cls.run.func_code.co_varnames[2:cls.run.func_code.co_argcount]:
			yield cls.get_constraint(name)
