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
from devparrot.core import session, modules
import re, os, types

_config = None

class Option(object):
    def __init__(self, name, config, parent, type="string"):
        self.name = name
        self.config = config
        self.parent = parent
        self.type = type
        self.values = {}

    def get(self, keys=[None]):
        if None not in keys:
            keys.append(None)
        for key in keys:
            if key in self.values:
                return self.values[key]
        raise KeyError("No Value for option named %s"%self.name)

    def set(self, value, key=None):
        try:
            old = self.values[key]
        except KeyError:
            old = None
        self.values[key] = value
        session.eventSystem.event("configChanged")(self, old)

    def update(self, values):
        if not isinstance(values, dict):
            values = {None:values}
        self.values.update(values)

class ReadOnlyOption(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def get(self, *args, **kwords):
        return self.value

class BaseSection(object):
    def __init__(self, config):
        self.config = config
        self.options = {}

    def _get(self, name):
        return self.options[name]

    def add_option(self, name, type="string", **kwords):
        self.options[name] = Option(name, self.config, self, type)
        if "default" in kwords:
            self.options[name].set(kwords["default"])

    def add_section(self, name):
        self.options[name] = Section(self.config, self)

    def update(self, options, skip_unknown=False):
        for key, value in options.items():
            if key[0] == "_":
                continue
            try:
                self.options[key].update(value)
            except KeyError:
                if not skip_unknown:
                    raise
                print("%s is not a valid option name"%key)

class Section(BaseSection):
    def __init__(self, config, parent):
        BaseSection.__init__(self, config)
        self.parent = parent

class Config(BaseSection):
    def __init__(self):
        BaseSection.__init__(self, self)

    def get(self, name, keys=[None]):
        names = name.split('.')
        sections, name = names[:-1], names[-1]
        section = self
        for sectionName in sections:
            section = section._get(sectionName)
        option = section._get(name)
        return option.get(keys)

    def __getattr__(self, name):
        return self._get(name)

    __getitem__ = __getattr__

class ConfigFile(object):
    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        options = {}
        globals_ = {'source' : self.source_file}
        execfile(self.filename, globals_, options)
        return options

    def source_file(self, filename):
        pass

class ConfigParser(object):
    def __init__(self, config):
        self.config = config
        self.configFiles = []

    def add_file(self, filename):
        self.configFiles.append(ConfigFile(filename))

    def parse(self):
        for configFile in self.configFiles:
            options = configFile.parse()
            self.config.update(options, skip_unknown=True)

def init(cmd_options):
    import os
    global _config
    devparrotPath = os.path.dirname(os.path.dirname(os.path.abspath(os.path.realpath(__file__))))
    _config = Config()
    _config.add_option("encoding", default="utf8")
    _config.add_option("wchars", default=u"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ€")
    _config.add_option("spacechars", default=u" \t")
    _config.add_option("puncchars", default=u"!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿×÷")

    _config.add_option("default_controllers", default=[ 'CarretController', 'KeyboardController', 'MouseController' ])

    _config.add_option("window_height", type='int', default=600)
    _config.add_option("window_width", type='int', default=800)
    _config.add_option("window_x", type='int', default=10)
    _config.add_option("window_y", type='int', default=10)

    _config.add_option("auto_indent", default=True)
    _config.add_option("remove_tail_space", default=True)
    _config.add_option("tab_width", type='int', default=4)
    _config.add_option("space_indent", default=False)
    _config.add_option("highlight_current_line", default=True)
    _config.add_option("show_line_numbers", default=True)
    _config.add_option("smart_home_end", default=True)
    _config.add_option("font", default="monospace")

    _config.add_option("invalid_color", default="red")
    _config.add_option("ok_color", default="#BBFFBB")
    _config.add_option("error_color", default="#FF9999")
    _config.add_option("highlight_tag_color", default="#FFFFBB")
    _config.add_option("search_tag_color", default="#FFAAAA")
    _config.add_option("currentLine_tag_color", default="#EEEEEE")

    _config.add_option("menuBar", default=[("File", [ ("New", "new"),
                    ("Open", "open"),
                    "---",
                    ("Save", "save"),
                    ("Save as", "saveas")
                  ]),
         ("Edit", [ ("Undo", "undo"),
                    ("Redo", "redo"),
                    "---",
                    ("Copy", "copy"),
                    ("Cut", "cut"),
                    ("Paste", "paste")
                  ]),
         ("Help", "help")
        ])
    _config.add_option("popupMenu", default=[ ("Undo", "undo"),
            ("Redo", "redo"),
            "---",
            ("Copy", "copy"),
            ("Cut", "cut"),
            ("Paste", "paste")
          ])

    _config.add_option("start_command", default="open %%config(ARGUMENTS)")

    modules.update_config(_config)

    parser = ConfigParser(_config)
    parser.add_file(os.path.expanduser("~/.devparrotrc"))
    parser.parse()

    dict.__setitem__(_config.options, 'ARGUMENTS', ReadOnlyOption('ARGUMENTS', cmd_options.ARGUMENTS))
    dict.__setitem__(_config.options, 'devparrotPath', ReadOnlyOption('devparrotPath', devparrotPath))

    return _config

def load(cmd_options):
    for line in _config.start_command.get().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        session.commandLauncher.run_command_nofail(line)
