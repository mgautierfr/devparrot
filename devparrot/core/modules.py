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

import os

def init(path):
    path = os.path.join(path, 'modules')
    moduleList = os.listdir(path)
    for module in moduleList:
        m = load_module(path, module)
        if m:
            m.activate()
    pass

def load_module(path, name):
    import imp
    if name.endswith('.pyc'):
        return
    if name.endswith('.py'):
        name = name[:-3]

    try:
        fp, pathname, description = imp.find_module(name, [path])
    except ImportError, m:
        print m
        return

    try:
        return imp.load_module(name, fp, pathname, description)
    finally:
        # Since we may exit via an exception, close fp explicitly.
        if fp:
            fp.close()






