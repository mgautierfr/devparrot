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


from . import documentManager
from . import commandLauncher as _commandLauncher
import logging
from . import userLogging
from .utils import event
from . import help

window = None
helperManager = None
_documentManager = None
_workspace = None
_globalContainer = None
config = None
commands = None
macros = None
modules = {}
memories = {}
controllers = {}
bindings = None
completionSystem = None
help_entries = help.HelpSection(None, "devparrot", "Devparrot help")

eventSystem = event.EventSource()

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
    global _documentManager
    global commandLauncher
    global bindings
    global macros

    _documentManager = documentManager.DocumentManager()
    commandLauncher = _commandLauncher.CommandLauncher()
    _commandLauncher.create_section()
    bindings = bind.Binder()
    macros = Section(None, None)

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

