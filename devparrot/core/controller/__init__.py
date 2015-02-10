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


import tkinter
import collections

PREFIX = "tkController"

def bind(*events):
    def decorator(func):
        func.tkevent = events
        return func
    return decorator

class Modifiers:
    _shift, _lock, _ctrl, _alt, _numlock, _meta, _super, _altgr, _button1, _button2, _button3, _unknown1, _unknown2, _unknown3, _unknown4 = (2**i for i in range(0, 15))
    # _unknown2 seems to be activate when we are in alternate keymap (in linux/X/gnome)
    def __init__(self, event):
        state = event.state
        self.modifiers = set()
        for level in [2**i for i in range(15, -1, -1)]:
            if state >= level:
                self.modifiers.add(level)
                state -= level
            

    def __getattr__(self, name):
        level = getattr(self, "_"+name)
        return level in self.modifiers

class MetaController(type):
    def __new__(cls, name, bases, dct):
        _class = type.__new__(cls, name, bases, dct)
        if name != "Controller":
            from devparrot.core import session
            ctrl = _class()
            session.add_controller(name, ctrl)
        return _class
            

class Controller(metaclass=MetaController):
    def __init__(self):
        self.tag = str(self.__class__.__name__)
        self.configure()
    
    def configure(self):
        def bind(event, handler):
            tkinter._default_root.bind_class(self.tag, event, handler)
        for key in dir(self):
            method = getattr(self, key)
            if hasattr(method, "tkevent") and isinstance(method, collections.Callable):
                for eventSequence in method.tkevent:
                    bind(eventSequence,
                           lambda event, method=method: method(event, Modifiers(event))
                          )


def load():
    from pwd import getpwuid
    import os
    from devparrot.core import session
    path = os.path.join(session.config.get('devparrotPath'), "controllers")
    load_directory(path)

    _homedir = getpwuid(os.getuid())[5]
    path = os.path.join(_homedir,'.devparrot', 'controllers')
    load_directory(path)

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
