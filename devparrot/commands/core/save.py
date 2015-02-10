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
from devparrot.core.constraints import OpenDocument, File


@Command(
_section='core',
document=OpenDocument(help="document to save"),
fileName=File(mode=File.SAVE)
)
def save(document, fileName):
    from devparrot.core import session
    from devparrot.core.errors import ContextError
    try:
        if document.has_a_path() and document.get_path() == fileName:
            document.write()
            return
    
        # we've ask to change the path
        if session.get_documentManager().has_file(fileName):
            #The document is already opened.
            #do nothing (should warn or save/close/reopen)
            raise ContextError("{} is already open and is not the file you want to save".format(fileName))
    
        from devparrot.documents import FileDocSource
        session.eventSystem.event('pathAccess')(fileName)
        session.get_documentManager().del_file(document)
        document.set_path(FileDocSource(fileName, guess_encoding=False))
        session.get_documentManager().add_file(document)
        document.write()
    except IOError:
        raise FileAccessError(fileName)
