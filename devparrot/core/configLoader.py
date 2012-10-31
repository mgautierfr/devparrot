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

from devparrot.core.utils.variable import CbCaller

_config = None

class ModuleWrapper(object):
    def __init__(self, config):
        object.__setattr__(self, 'config', config)

    def __getattr__(self, name):
        return getattr(self.config, name)

    def __setattr__(self, name, value):
        return self.config.__setattr__(name, value)

class _Section(CbCaller):
    def __init__(self):
        from devparrot.core.utils.variable import CbList
        # do not call parent __init__
        object.__setattr__(self, "_callbacks", CbList())
        object.__setattr__(self, "sections", {})
        object.__setattr__(self, "variables", {})

    def __getattr__(self, name):
        try:
            return self.variables[name]
        except KeyError:
            try:
                return self.sections[name]
            except KeyError:
                raise AttributeError

    def get(self, name):
        args = name.split('.')
        return self._get(args)

    def _get(self, nameList):
        first = getattr(self, nameList[0])
        if len(nameList) == 1:
            return first.get()
        return first._get(nameList[1:])

    def add_section(self, name, section):
        self.sections[name] = section

    def add_variable(self, name, value):
        from devparrot.core.utils.variable import Variable
        if isinstance(value, Variable):
            self.variables[name] = value
        else:
            self.variables[name] = Variable(value)

    def __str__(self):
        return "Section named %s" % type(self)
    
    def notify(self):
        for var in self.variables:
            CbCaller.notify(self, var, var)
        for section in self.sections:
            section.notify()

class Section(_Section):
    def __init__(self, config):
        _Section.__init__(self)
        object.__setattr__(self, "config", config)

    def __setattr__(self, name, value):
        if name in self.sections:
            print "WARNING: can't redifine section name %s"%name
            return

        if name not in self.variables:
            print "WARNING: %s is not a valid (known) variables name in section %s"%(name, context)
            return

        variable = self.variables[name].set(value)

    def __enter__(self):
        self.config.set_currentContext(self)
        return self

    def __exit__(self, *args):
        self.config.unset_currentContext()
        

class Config(_Section):
    def __init__(self):
        _Section.__init__(self)
        object.__setattr__(self, "contexts", [])

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

    def __setattr__(self, name, value):
        try:
            context = self.contexts[-1]
        except IndexError:
            context = self
        if name in context.sections:
            print "WARNING: can't redifine section name %s"%name
            return

        if name not in context.variables:
            print "WARNING: %s is not a valid (known) variables name in section %s"%(name, context)
            return

        variable = context.variables[name].set(value)

    def set_currentContext(self, section):
        self.contexts.append(section)

    def unset_currentContext(self):
        self.contexts.pop()

def init():
    from devparrot.controllers.defaultControllerMode import DefaultControllerMode
    global _config
    _config = Config()
    _config.add_variable("controller", DefaultControllerMode())
    section = createSection("window")
    section.add_variable("height", 600)
    section.add_variable("width", 800)
    section = createSection("textView")
    section.add_variable("auto_indent", True)
    section.add_variable("remove_tail_space", True)
    section.add_variable("tab_width", 4)
    section.add_variable("space_indent", False)
    section.add_variable("highlight_current_line", True)
    section.add_variable("show_line_numbers", True)
    section.add_variable("smart_home_end", True)
    section.add_variable("font", "monospace")
    section.add_variable("hlstyle", "default")
    section = createSection("color")
    section.add_variable("notFoundColor", "red")
    section.add_variable("okColor", "#BBFFBB")
    section.add_variable("errorColor", "#FF9999")
    section.add_variable("highlight_tag_color", "#FFFFBB")
    section.add_variable("search_tag_color", "#FFAAAA")
    section.add_variable("currentLine_tag_color", "#EEEEEE")

def createSection(name, parent=None):
    if not parent:
        parent = _config
    newSection = Section(_config)
    parent.add_section(name, newSection)
    return newSection

def load():
    from pwd import getpwuid
    import os
    from devparrot.core import command, capi
    _homedir = getpwuid(os.getuid())[5]
    _user_config_path = os.path.join(_homedir,'.devparrot')

    _global = {'binds':command.binder,
               'Command':command.baseCommand.Command,
               'constraints':command.constraints,
               'capi':capi,
               'config': _config
              }

    execfile(_user_config_path, _global, _config)
    return _config

