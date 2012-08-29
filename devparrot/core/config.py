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

from collections import MutableMapping

import os, pwd
import sys

import command

from devparrot.controllers.defaultControllerMode import DefaultControllerMode
from devparrot.core.utils.variable import Property, Variable, CbCaller, CbList


class ModuleWrapper(object):
	def __init__(self, config):
		object.__setattr__(self, 'config', config)

	def __getattr__(self, name):
		return getattr(self.config, name)

	def __setattr__(self, name, value):
		return self.config.__setattr__(name, value)

class Section(CbCaller):
	def __init__(self):
		object.__setattr__(self, "_callbacks", CbList())

	def __setattr__(self, name, value):
		raise RuntimeError("You can't add a attribute to a section before adding it to the config (or a subSection)")
	
	def __str__(self):
		return "Section named %s"%type(self)
	
	@property
	def variables(self):
		return (getattr(self,name) for name in dir(self)
		                   if name.startswith("_")
		                   and isinstance(getattr(self, name), Variable))
	
	def notify(self):
		for var in self.variables:
			CbCaller.notify(self, var, var)
			

class _ValidSection(Section):
	def __init__(self):
		Section.__init__(self)

	def __setattr__(self, name, value):
		if value.__class__ == Section:
			# we create a new class for each a section
			# this way, we can add different properties for each a section
			perSectionClass = type("Section%s"%name, (_ValidSection,), {})
			newSection = perSectionClass()
			object.__setattr__(self, name, newSection)
			return
		
		variable = getattr(self, "_"+name, None)
		if variable is None:
			(pro, notify, register, unregister) = Property(name)
			setattr(type(self), name, pro)
			setattr(type(self), name+"_notify", notify)
			setattr(type(self), name+"_register", register)
			setattr(type(self), name+"_unregister", unregister)
			if isinstance(value, Variable):
				object.__setattr__(self, "_"+name, value)
			else:
				object.__setattr__(self, "_"+name, Variable(value))
		else:
			variable.set(value)

class Config(_ValidSection):
	def __init__(self):
		_ValidSection.__init__(self)

	def __getitem__(self, name):
		try:
			return getattr(self, name)
		except AttributeError:
			raise KeyError

	def __setitem__(self, name, value):
		setattr(self, name, value)
	
	def __delitem__(self, name):
		delattr(self, name)

	def __iter__(self, *args, **kwords):
		return self.__dict__.__iter__(*args, **kwords)

	def __len__(self):
		return self.__dict__.__len__()
		

_homedir = pwd.getpwuid(os.getuid())[5]
_user_config_path = os.path.join(_homedir,'.devparrot')
_default_config_path = os.path.dirname(os.path.realpath(__file__))
_default_config_path = os.path.join(_default_config_path,"../../resources/default_config")

_config = Config()
mdWrapper = ModuleWrapper(_config)
_global = {'Section':Section,
           'binds':command.binder,
           'Command':command.baseCommand.Command,
           'constraints':command.constraints,
           'capi':command.capi,
           'DefaultControllerMode' : DefaultControllerMode,
           'config': mdWrapper
          }

execfile(_default_config_path, _global, _config)
execfile(_user_config_path, _global, _config)

sys.modules[__name__] = mdWrapper

