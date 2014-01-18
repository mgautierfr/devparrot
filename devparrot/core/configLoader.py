# -*- coding: utf8 -*-
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


from devparrot.core.utils.variable import CbCaller
import re, os

_config = None

class Section(CbCaller):
    def __init__(self, config, name):
        from devparrot.core.utils.variable import CbList
        # do not call parent __init__
        object.__setattr__(self, "_callbacks", CbList())
        object.__setattr__(self, "sections", {})
        object.__setattr__(self, "variables", {})
        object.__setattr__(self, "config", config)
        object.__setattr__(self, "name", name)

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
    
    def notify(self):
        for var in self.variables:
            CbCaller.notify(self, var, var)
        for section in self.sections:
            section.notify()

    def __setattr__(self, name, value):
        from devparrot.core.session import logger
        if name in self.sections:
            logger.warning("can't redifine section name %s", name)
            return

        if name not in self.variables:
            logger.warning("%s is not a valid (known) variables name in section %s", name, self)
            return

        self.variables[name].set(value)


    def __str__(self):
        return self.name

class Config(Section):
    def __init__(self):
        Section.__init__(self, self, "config")

    def __setitem__(self, name, value):
        setattr(self, name, value)

def init(cmd_options):
    from devparrot.controllers.defaultControllerMode import DefaultControllerMode, DefaultROControllerMode
    import os
    global _config
    devparrotPath = os.path.dirname(os.path.dirname(os.path.abspath(os.path.realpath(__file__))))
    _config = Config()
    _config.add_variable("controller", DefaultControllerMode())
    _config.add_variable("ROcontroller", DefaultROControllerMode())
    _config.add_variable("devparrotPath", devparrotPath)
    _config.add_variable("wchars", u"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ€")
    _config.add_variable("spacechars", u" \t")
    _config.add_variable("puncchars", u"!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿×÷")
    section = createSection("cmd")
    section.add_variable("ARGUMENTS", cmd_options.ARGUMENTS)

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
    newSection = Section(_config, name)
    parent.add_section(name, newSection)
    return newSection

def load(cmd_options):
    from devparrot.core import session

    if cmd_options.load_configrc:
        try:
            with open(cmd_options.configrc) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    session.commandLauncher.run_command_nofail(line)
        except IOError:
            session.logger.warning("Cannot load %r config file", cmd_options.configrc)
