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

ActionList = list()

import types

class MetaAction(type):
	def __new__(cls, name, bases, dct):
		for (key, value) in dct.items():
			if isinstance(value, types.FunctionType):
				dct[key] = classmethod(value)
		return type.__new__(cls, name, bases, dct)

	def __init__(cls, name, bases, dct):
		super(MetaAction, cls).__init__(name, bases, dct)
		if name != "Action":
			ActionList.append(cls)


class Action:
	__metaclass__ = MetaAction

	def callback(cls, accel_group, acceleratable, keyval, modifier):
		return cls.run()

	def defaultChecker(cls, line):
		if line.startswith(cls.__name__):
			return line.split(' ')[1:]
		return None

	def regChecker(cls, line):
		return cls.defaultChecker(line)
		
