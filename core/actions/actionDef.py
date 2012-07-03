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
			import core.controler
			core.controler.add_alias(name, cls, 0)

class Action:
	__metaclass__ = MetaAction

	def pre_check(cls, cmdText):
		return True
	
	def get_argNumber(cls):
		return cls.run.func_code.co_argcount-2
		
	def get_argName(cls, index):
		return cls.run.func_code.co_varnames[index+2]

	def get_constraint(cls, name):
		constraint = cls.__dict__.get(name, constraints.Default()) 
		constraint.init()
		return constraint
		
	def get_allConstraints(cls):
		for name in cls.run.func_code.co_varnames[2:cls.run.func_code.co_argcount]:
			yield cls.get_constraint(name)
		
		
		
		
