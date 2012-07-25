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


class ModuleWrapper(object):
	def __init__(self, config):
		object.__setattr__(self, 'config', config)

	def __getattr__(self, name):
		return getattr(self.config, name)

	def __setattr__(self, name, value):
		return self.config.__setattr__(name, value)

class Config(object):
	def __init__(self, *args, **kwords):
		pass

	def __getitem__(self, name):
		try:
			return object.__getattribute__(self, name)
		except AttributeError:
			raise KeyError

	def __setitem__(self, name, value):
		object.__setattr__(self, name, value)

	def __delitem__(self, name):
		self.values.__delattr__(name)

	def __iter__(self, *args, **kwords):
		return self.__dict__.__iter__(*args, **kwords)

	def __len__(self):
		return self.__dict__.__len__()

class Section(object):
	def __init__(self):
		pass

	def __setattr__(self, name, value):
		object.__setattr__(self, name, value)

_homedir = pwd.getpwuid(os.getuid())[5]
_user_config_path = os.path.join(_homedir,'.devparrot')
_default_config_path = os.path.dirname(os.path.realpath(__file__))
_default_config_path = os.path.join(_default_config_path,"../../resources/default_config")

_config = Config()
_global = {'Section':Section,
           'binds':command.binder,
           'Command':command.baseCommand.Command,
           'constraints':command.constraints,
           'capi':command.capi
          }

execfile(_default_config_path, _global, _config)
execfile(_user_config_path, _global, _config)

sys.modules[__name__] = ModuleWrapper(_config)

