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


from devparrot.capi import Command, Alias, get_currentDocument
from devparrot.core.session import bindings

@Alias()
def cut():
    """cut selection to clipboard"""
    return "section sel | memory CLIPBOARD\nstream.empty | section sel"

@Alias()
def copy():
    """copy selection to clipboard"""
    return "section sel | memory CLIPBOARD"

@Alias()
def paste():
    """paste clipboard content at "insert" mark"""
    return "memory CLIPBOARD | section sel"

@Alias()
def undo():
    """undo last command"""
    get_currentDocument().get_model().undo()

@Command()
def redo():
    """redo last undone command"""
    get_currentDocument().get_model().redo()

bindings["<<Cut>>"] = "cut\n"
bindings["<<Copy>>"] = "copy\n"
bindings["<<Paste>>"] = "paste\n"
