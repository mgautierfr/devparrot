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

from devparrot.core import session

_modules = {}

def load():
    from pwd import getpwuid
    import os
    path = os.path.join(session.config.get('devparrotPath'), 'modules')
    moduleList = os.listdir(path)
    for module in moduleList:
        load_module(path, module)

    _homedir = getpwuid(os.getuid())[5]
    path = os.path.join(_homedir,'.devparrot', 'modules')
    if os.path.exists(path):
        moduleList = os.listdir(path)
        for module in moduleList:
            load_module(path, module)

def load_module(path, name):
    import imp, os
    import configLoader
    if name.endswith('.py'):
        name = name[:-3]
    elif not os.path.isdir(os.path.join(path,name)):
        return

    try:
        fp, pathname, description = imp.find_module(name, [path])
    except ImportError, err:
        print err
        return

    with fp:
        module = imp.load_module(name, fp, pathname, description)
        _modules[name] = module
        section = configLoader.createSection(name, session.config.modules)
        section.add_variable("active", False)
        module.init(section, name)


