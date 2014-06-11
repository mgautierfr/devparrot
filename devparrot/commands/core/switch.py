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
from devparrot.core.constraints import OpenDocument

@Command(
_section='core',
document = OpenDocument()
)
def switch(document):
    """set focus to document"""
    from devparrot.core import session
    if document == None:
        session.get_currentContainer().set_documentView(None)
    elif document.documentView.is_displayed():
        document.documentView.parentContainer.select(document.documentView)
        document.documentView.focus()
    else:
        session.get_currentContainer().set_documentView(document.documentView)
        document.documentView.focus() 
