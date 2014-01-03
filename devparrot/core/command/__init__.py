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


__all__ = ['Command', 'Alias', 'MasterCommand', 'SubCommand', 'Macro']

from decorators import Command, Alias, MasterCommand, SubCommand, Macro

def load():
    from pwd import getpwuid
    import os
    from devparrot.core import session
    path = os.path.join(session.config.get('devparrotPath'), "commands")
    moduleList = os.listdir(path)
    for module in moduleList:
        load_module(path, module)

    _homedir = getpwuid(os.getuid())[5]
    path = os.path.join(_homedir,'.devparrot', 'commands')
    if os.path.exists(path):
        moduleList = os.listdir(path)
        for module in moduleList:
            load_module(path, module)

def load_module(path, name):
    import imp, os
    if name.endswith('.py'):
        name = name[:-3]
    elif not os.path.isdir(os.path.join(path,name)):
        return

    try:
        fp, pathname, description = imp.find_module(name, [path])
    except ImportError, err:
        session.logger.error("can't import module named %s", name)
        return

    with fp:
        return imp.load_module(name, fp, pathname, description)



