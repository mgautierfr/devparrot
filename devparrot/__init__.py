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


"""
This is the main module of devparrot
"""

import sys
import os
import argparse
from ast import literal_eval

from . import core


def info(type, value, tb):
    import traceback, pdb
    traceback.print_exception(type, value, tb)
    print()
    pdb.pm()

def handle_pdb(sig, frame):
    import pdb
    pdb.Pdb().set_trace(frame)

def option_split(string):
    name, value =  string.split(',', maxsplit=1)
    try:
        value = literal_eval(value)
    except ValueError:
        pass
    return name, value

def parse_commandLine(args=sys.argv):
    parser = argparse.ArgumentParser(description="The Devparrot IDE. The one")
    parser.add_argument("call_name",
                        type=os.path.basename,
                        help=argparse.SUPPRESS)
    parser.add_argument("--configrc",
                        default=os.path.expanduser("~/.devparrotrc"),
                        help="The rc file to load")
    parser.add_argument("--no_configrc",
                        dest="load_configrc",
                        action='store_false',
                        help="Do not load rc file")
    debug_group = parser.add_argument_group("debug", "Option to debug Devparrot itself")
    debug_group.add_argument("--debug",
                        dest="debug",
                        action='store_true',
                        help="Run in debug mode")
    debug_group.add_argument("--profile",
                        dest="profile",
                        action='store_true',
                        help="Profile the execution"),
    parser.add_argument("--option", "-o", dest="options",
                        action="append",
                        type=option_split,
                        default=[])
    options, args = parser.parse_known_args(args)
    options.ARGUMENTS = args
    return options

def set_signal_handler():
    import signal
    print("running in debug mode")
    sys.excepthook = info
    signal.signal(signal.SIGUSR1, handle_pdb)

def _main(cmd_options):
    os.environ['XMODIFIERS'] = "@im=none"
    core.session.init()
    config = core.configLoader.init(cmd_options)
    core.session.set_config(config)
    core.ui.init()
    core.modules.load()
    core.command.load()
    core.controller.load()
    core.modules.activate_modules()
    core.textCompletion.init()
    core.configLoader.run_startup_commands(config.start_command.get())
    core.session.window.mainloop()


def main():
    cmd_options = parse_commandLine()
    if cmd_options.debug:
        set_signal_handler()
    if cmd_options.profile:
        import cProfile, pstats, io
        pr = cProfile.Profile()
        pr.enable()
        try:
            ret = _main(cmd_options)
        finally:
            pr.disable()
            s = io.StringIO()
            sortby = 'cumulative'
            ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            ps.print_stats()
            print(s.getvalue())
    else:
        return _main(cmd_options)
