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


from devparrot.core.command import Command
from devparrot.core import session
from devparrot.core.session import bindings
from devparrot.core.constraints import OpenDocument, Range, Index, Default

@Command(
what = Range(default=Range.DEFAULT('sel'), help="The range to cut")
)
def cut(what):
    """cut a range of text to clipboard

    This means also removing it from the buffer"""
    content = session.commands.section(what)
    session.commands.memory('CLIPBOARD', content)
    session.commands.section(what, session.commands.stream.empty())

@Command(
what = Range(default=Range.DEFAULT('sel'), help="The range to copy")
)
def copy(what):
    """copy a range of text to clipboard"""
    content = session.commands.section(what)
    session.commands.memory('CLIPBOARD', content)

@Command(
where = Range(default=Range.DEFAULT('sel'), help="Where to insert the text from the clipboard")
)
def paste(where):
    """paste clipboard content at the "where" position."""
    content = session.commands.memory('CLIPBOARD')
    session.commands.section(where, content)

@Command(document=OpenDocument(default=OpenDocument.CURRENT), help="The document on which do the undo")
def undo(document):
    """undo last command"""
    document.get_model().undo()

@Command(document=OpenDocument(default=OpenDocument.CURRENT), help="The document on which do the redo")
def redo(document):
    """redo last undone command"""
    document.get_model().redo()

bindings["<<Cut>>"] = "cut\n"
bindings["<<Copy>>"] = "copy\n"
bindings["<<Paste>>"] = "paste\n"
