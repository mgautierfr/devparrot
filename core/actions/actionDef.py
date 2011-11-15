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
		dct['accelerators'] = list()
		for (key, value) in dct.items():
			if isinstance(value, types.FunctionType):
				cm = classmethod(value)
				if 'accelerators' in value.func_dict:
					for accel in value.func_dict['accelerators']:
						accel.set_function(cm)
						dct['accelerators'].append(accel)
				dct[key] = cm

		return type.__new__(cls, name, bases, dct)

	def __init__(cls, name, bases, dct):
		super(MetaAction, cls).__init__(name, bases, dct)
		if name != "Action":
			for accel in cls.accelerators:
				accel.set_cls(cls)
			ActionList.append(cls)

class Accelerator:
	def __init__(self, accelerator, datas=()):
		from types import StringTypes
		if isinstance(accelerator, StringTypes):
			#from gtk import accelerator_parse
			#self.accelerator = accelerator_parse(accelerator)
			pass
		else:
			self.accelerator = accelerator
		self.datas = datas

	def set_cls(self, cls):
		self.cls = cls

	def set_function(self, function):
		self.function = function

#	def connect_group(self, accelGroup):
#		accelGroup.connect_group(self.accelerator[0],self.accelerator[1],
#		                         accel_flags=0,
#		                         callback = self)

	def __call__(self, accel_group, acceleratable, keyval, modifier):
		import core.controler
		return core.controler.run_action(self.cls.__name__, self.function.__get__(None, self.cls),*self.datas)

class accelerators:
	def __init__(self, *accelerators):
		self.accelerators = accelerators

	def __call__(self, func):
		func.accelerators=self.accelerators
		return func

class Action:
	__metaclass__ = MetaAction

	def defaultChecker(cls, line):
		command = line.split(' ')[0]
		if command == cls.__name__:
			return line.split(' ')[1:]
		return None

	def regChecker(cls, line):
		return cls.defaultChecker(line)
		
