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
from devparrot.core.constraints import File

@Command(
_section = 'core',
files = File(mode=(File.OPEN, File.NEW), help="a list of file to open")
)
def open(*files):
    """
    Open a existing or new file
    """
    for fileToOpen in files:
        _open_a_file(fileToOpen)

def _open_a_file(fileToOpen):
    from devparrot.core import session
    if not fileToOpen: return False
    if session.get_documentManager().has_file(fileToOpen):
        doc = session.get_documentManager().get_file(fileToOpen)
    else:
        from devparrot.core.errors import FileAccessError
        from devparrot.core.document import Document
        from devparrot.documents.fileDocSource import FileDocSource
        try:
            doc = Document(FileDocSource(fileToOpen))
            session.get_documentManager().add_file(doc)
            doc.load()
        except IOError:
            raise FileAccessError(fileToOpen)
    session.commands.core.switch(doc)
