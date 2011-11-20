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

class MetaAction(type):
	def __new__(cls, name, bases, dct):
		#dct['accelerators'] = list()
		for (key, value) in dct.items():
			if isinstance(value, types.FunctionType):
				cm = classmethod(value)
				#if 'accelerators' in value.func_dict:
				#	for accel in value.func_dict['accelerators']:
				#		accel.set_function(cm)
				#		dct['accelerators'].append(accel)
				dct[key] = cm

		return type.__new__(cls, name, bases, dct)

	def __init__(cls, name, bases, dct):
		super(MetaAction, cls).__init__(name, bases, dct)
		if name != "Action":
			import core.controler
			import re
			core.controler.add_alias(re.compile(r"%s"%name), cls, 0)
			#for accel in cls.accelerators:
			#	accel.set_cls(cls)
if False:
#class Accelerator:
	def __init__(self, accelerator, datas=()):
		self.accelerator = accelerator
		self.datas = datas

	def set_cls(self, cls):
		self.cls = cls

	def set_function(self, function):
		self.function = function
	
	def bind(self, name):
		event.add("<<name>>",self.accelerator)

	def __call__(self, accel_group, acceleratable, keyval, modifier):
		import core.controler
		return core.controler.run_action(self.cls.__name__, self.function.__get__(None, self.cls),*self.datas)

class Action:
	__metaclass__ = MetaAction
		
	def run(cls, *args):
		if args[0] in self.__dict__:
			self.__dict__[args[0]](*args[1:])