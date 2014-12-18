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


import documentManager
import commandLauncher as _commandLauncher
import logging
import userLogging
import utils.event
import help

_documentManager = documentManager.DocumentManager()
_workspace = None
_globalContainer = None
config = None
commands = None
macros = None
modules = None
memories = {}
controllers = {}
bindings = None
help_entries = {'devparrot':help.DevparrotHelp()}

eventSystem = utils.event.EventSource()

userLogger = userLogging.UserLogger()

logger = logging.getLogger("devparrot")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def init():
    from devparrot.core.command import bind
    from devparrot.core.command.section import Section
    from devparrot.core import modules as _modules
    global _documentManager
    global commandLauncher
    global bindings
    global macros
    global modules
    _documentManager = documentManager.DocumentManager()
    commandLauncher = _commandLauncher.CommandLauncher()
    _commandLauncher.create_section()
    bindings = bind.Binder()
    macros = Section(None, None)
    modules = _modules._modules

def set_config(_config):
    global config
    config = _config

def get_documentManager():
    return _documentManager

def get_currentDocument():
    try:
        return _workspace.get_currentDocument()
    except AttributeError:
        return None

def set_workspace(workspace):
    global _workspace
    _workspace = workspace
   
def get_workspace():
    return _workspace
    
def set_globalContainer(globalContainer):
    global _globalContainer
    _globalContainer = globalContainer
   
def get_globalContainer():
    return _globalContainer

def get_currentContainer():
    return _workspace.get_currentContainer()

def add_controller(name, contr):
    controllers[name] = contr

