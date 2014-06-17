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

import core


def info(type, value, tb):
    import traceback, pdb
    traceback.print_exception(type, value, tb)
    print
    pdb.pm()

def handle_pdb(sig, frame):
    import pdb
    pdb.Pdb().set_trace(frame)


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
    parser.add_argument("--debug",
                        dest="debug",
                        action='store_true',
                        help="Run in debug mode")
    options, args = parser.parse_known_args(args)
    options.ARGUMENTS = args
    return options

def set_signal_handler():
    import signal
    print "running in debug mode"
    sys.excepthook = info
    signal.signal(signal.SIGUSR1, handle_pdb)

def _main(cmd_options):
    os.environ['XMODIFIERS'] = "@im=none"
    config = core.configLoader.init(cmd_options)
    core.session.init(config)
    core.ui.init()
    core.modules.load()
    core.command.load()
    core.controller.load()
    core.configLoader.load(cmd_options)

    core.ui.window.mainloop()


def main():
    cmd_options = parse_commandLine()
    if cmd_options.debug:
        set_signal_handler()
    return _main(cmd_options)
