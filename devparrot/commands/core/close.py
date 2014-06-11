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
from devparrot.core import session

@Command(
_section='core',
document=OpenDocument(default=session.get_currentDocument, help="documents to close")
)
def close(document):
    from devparrot.core.ui import viewContainer
    if document.documentView.is_displayed():
        parentContainer = document.documentView.get_parentContainer()
        parentContainer.detach_child(document.documentView)
        if parentContainer.get_nbChildren() == 0:
            viewContainer.unsplit(parentContainer)
    return session.get_documentManager().del_file(document)
