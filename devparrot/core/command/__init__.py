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

from .decorators import Command, Alias, MasterCommand, SubCommand, Macro

def load():
    from pwd import getpwuid
    import os
    from devparrot.core import session
    path = os.path.join(session.config.get('devparrotPath'), "commands")
    load_directory(path)

    for dir_ in session.config.get('custom_commands_dir'):
        dir_ = os.path.expanduser(dir_)
        dir_ = os.path.expandvars(dir_)
        dir_ = os.path.abspath(dir_)
        load_directory(dir_)

def load_directory(path):
    import os.path
    if os.path.exists(path):
        moduleList = os.listdir(path)
        for module in moduleList:
            if os.path.isdir(os.path.join(path, module)):
                load_directory(os.path.join(path, module))
            else:
                load_module(path, module)

def load_module(path, name):
    import imp, os
    from devparrot.core import session
    if not name.endswith('.py'):
        return
    name = name[:-3]

    try:
        fp, pathname, description = imp.find_module(name, [path])
    except ImportError as err:
        session.logger.error("can't import module named %s in dir %s", name, path)
        return

    with fp:
        return imp.load_module(name, fp, pathname, description)


def arg_escape(arg):
    import codecs
    return codecs.encode(arg, "unicode_escape").decode()
