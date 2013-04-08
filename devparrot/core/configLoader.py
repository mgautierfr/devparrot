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

class _Section(CbCaller):
    def __init__(self):
        from devparrot.core.utils.variable import CbList
        # do not call parent __init__
        object.__setattr__(self, "_callbacks", CbList())
        object.__setattr__(self, "sections", {})
        object.__setattr__(self, "variables", {})

    def _get(self,name):
        try:
            return self.variables[name]
        except KeyError:
            return self.sections[name]

    def __getattr__(self, name):
        try:
            return self._get(name)
        except KeyError:
            raise AttributeError

    def __getitem__(self, name):
        return self._get(name)

    def get(self, name):
        args = name.split('.')
        section = self
        for arg in args[:-1]:
            section = section.sections[arg]
        return section._get(args[-1]).get()

    def set(self, name, value):
        args = name.split('.')
        section = self
        for arg in args[:-1]:
            section = section.sections[arg]
        section._get(args[-1]).set(value)

    def add_section(self, name, section):
        self.sections[name] = section

    def add_variable(self, name, value):
        from devparrot.core.utils.variable import Variable
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
            session.logger.warning("can't redifine section name %s", name)
            return

        if name not in self.variables:
            session.logger.warning("%s is not a valid (known) variables name in section %s", name, self)
            return

        self.variables[name].set(value)

class Config(_Section):
    def __init__(self):
        _Section.__init__(self)

    def __setitem__(self, name, value):
        setattr(self, name, value)

def init():
    from devparrot.controllers.defaultControllerMode import DefaultControllerMode, DefaultROControllerMode
    import os
    global _config
    devparrotPath = os.path.dirname(os.path.dirname(os.path.abspath(os.path.realpath(__file__))))
    _config = Config()
    _config.add_variable("controller", DefaultControllerMode())
    _config.add_variable("ROcontroller", DefaultROControllerMode())
    _config.add_variable("devparrotPath", devparrotPath)
    section = createSection("window")
    section.add_variable("height", 600)
    section.add_variable("width", 800)
    section.add_variable("posx", 10)
    section.add_variable("posy", 10)
    section = createSection("textView")
    section.add_variable("auto_indent", True)
    section.add_variable("remove_tail_space", True)
    section.add_variable("tab_width", 4)
    section.add_variable("space_indent", False)
    section.add_variable("highlight_current_line", True)
    section.add_variable("show_line_numbers", True)
    section.add_variable("smart_home_end", True)
    section.add_variable("font", "monospace")
    section = createSection("color")
    section.add_variable("invalidColor", "red")
    section.add_variable("okColor", "#BBFFBB")
    section.add_variable("errorColor", "#FF9999")
    section.add_variable("highlight_tag_color", "#FFFFBB")
    section.add_variable("search_tag_color", "#FFAAAA")
    section.add_variable("currentLine_tag_color", "#EEEEEE")
    section = createSection("modules")
    return _config

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
    homedir = getpwuid(os.getuid())[5]
    user_config_path = os.path.join(homedir,'.devparrotrc')

    _global = {'binds':command.binder}

    if os.path.exists(user_config_path):
        execfile(user_config_path, _global, _config)



