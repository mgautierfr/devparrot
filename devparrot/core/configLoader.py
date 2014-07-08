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
import cfgparse
import re, os, types

_config = None

def _customSet(self_, value, cfgfile=None, keys=None):
    if cfgfile is None:
        cfgfile=self_._userFile
    old = self_.get()
    self_.__class__.set(self_, value, cfgfile=cfgfile, keys=keys).parse()
    session.eventSystem.event("configChanged")(self_, old)

class Config(object):
    def __init__(self):
        self._parser = cfgparse.ConfigParser(allow_py=True, exception=True)
        self._userFile = self._parser.add_file(os.path.expanduser("~/.devparrotcfg"))

    def add_option(self, name, *args, **kwords):
        option = self._parser.add_option(name, *args, **kwords)
        option.set = types.MethodType(_customSet, option)
        option._userFile = self._userFile
        object.__setattr__(self, name, option)

    def add_file(self, filename):
        return self._parser.add_file(filename)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            return object.__setattr__(self, name, value)
        self[name].set(value)

    def __getitem__(self, name):
        return getattr(self, name)

    __setitem__ = __setattr__

    def get(self, name, keys=None):
        return self[name].get(keys)

class ReadOnlyOption(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def get(self, *args, **kwords):
        return self.value

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

    modules.update_config(_config)

    object.__setattr__(_config, 'ARGUMENTS', ReadOnlyOption('ARGUMENTS', cmd_options.ARGUMENTS))
    object.__setattr__(_config, 'devparrotPath', ReadOnlyOption('devparrotPath', devparrotPath))
    return _config

def load(cmd_options):

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
