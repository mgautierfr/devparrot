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


from devparrot.core import session, modules
from devparrot.core.utils.config import Config, ConfigParser, ReadOnlyOption, AutoCreateSection

import os

_config = None

def init(cmd_options):
    global _config
    devparrotPath = os.path.dirname(os.path.dirname(os.path.abspath(os.path.realpath(__file__))))
    _config = Config()
    _config.add_option("encoding", default="utf8")
    _config.add_option("wchars", default=u"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ€")
    _config.add_option("spacechars", default=u" \t")
    _config.add_option("puncchars", default=u"!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿×÷")

    _config.add_option("default_controllers", default=[ 'CarretController', 'KeyboardController', 'MouseController' ])

    _config.add_option("window_height", default=600)
    _config.add_option("window_width", default=800)
    _config.add_option("window_x", default=10)
    _config.add_option("window_y", default=10)

    _config.add_option("auto_indent", default=True)
    _config.add_option("remove_tail_space", default=True)
    _config.add_option("tab_width", default=4)
    opt = _config.add_option("space_indent", default=False)
    opt.set(False, keys=['Makefile'])
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

    _config.add_option("completion_functions", default="infile_completions")
    _config.add_option("completionName", default="BasicTextCompletor")

    dict.__setitem__(_config.options, 'hook', AutoCreateSection(_config, _config, 'hook'))

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
    parser.parse(with_dict={"bind":session.bindings})

    dict.__setitem__(_config.options, 'ARGUMENTS', ReadOnlyOption('ARGUMENTS', _config, _config, str, cmd_options.ARGUMENTS))
    dict.__setitem__(_config.options, 'devparrotPath', ReadOnlyOption('devparrotPath', _config, _config, str, devparrotPath))

    return _config

def load(cmd_options):
    for line in _config.start_command.get().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        session.commandLauncher.run_command_nofail(line)
