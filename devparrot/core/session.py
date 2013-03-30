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

import documentManager
import commandLauncher as _commandLauncher

_documentManager = documentManager.DocumentManager()
_workspace = None
_globalContainer = None
config = None
commands = {}

def init(_config):
    global config
    global _documentManager
    global commandLauncher
    config = _config
    _documentManager = documentManager.DocumentManager()
    commandLauncher = _commandLauncher.CommandLauncher()

def get_documentManager():
    return _documentManager

def get_currentDocument():
    return _workspace.get_currentDocument()

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

