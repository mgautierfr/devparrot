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

import ConfigParser
import os, pwd

config = None


_homedir = pwd.getpwuid(os.getuid())[5]
_user_config_path = os.path.join(_homedir,'.devparrot')
_default_config_path = os.path.dirname(os.path.realpath(__file__))
_default_config_path = os.path.join(_default_config_path,"../resources/default_config")

_config = ConfigParser.SafeConfigParser()
_config.read([_default_config_path, _user_config_path])


def get(section, option): return _config.get(section, option)

def getint(section, option): return _config.getint(section, option)

def getboolean(section, option) : return _config.getboolean(section, option)
