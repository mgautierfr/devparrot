#    This file is part of DevParrot.
#
#    Author: Matthieu Gautier <matthieu.gautier@devparrot.org>
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
#    Copyright 2011-2013 Matthieu Gautier


from devparrot.core.command import Command, Macro
from devparrot.core.constraints import ConfigEntry, Default

@Command(
_section='core',
_name='config',
configEntry = ConfigEntry(),
key=Default(default=lambda:"")
)
def configset(configEntry, value, key):
    """set a config entry to value"""
    from ast import literal_eval
    try:
        value = literal_eval(value)
    except (SyntaxError, ValueError):
        pass
    configEntry.set(value, keys=[key])

@Macro(
_name='config',
configEntry=ConfigEntry(),
key=Default(default=lambda:"")
)
def configget(configEntry, key):
    return configEntry.get(keys=key)
