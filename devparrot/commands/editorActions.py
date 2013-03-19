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

from devparrot.core.command.baseCommand import Command
from devparrot.core.command import binder
from devparrot.core import capi

@Command()
def cut():
    capi.currentDocument.get_currentView().cut_clipboard()

@Command()
def copy():
    capi.currentDocument.get_currentView().copy_clipboard()

@Command()
def paste():
    capi.currentDocument.get_currentView().paste_clipboard()

@Command()
def undo():
    capi.currentDocument.get_model().undo()

@Command()
def redo():
    capi.currentDocument.get_model().redo()

binder["<<Cut>>"] = "cut\n"
binder["<<Copy>>"] = "copy\n"
binder["<<Paste>>"] = "paste\n"
