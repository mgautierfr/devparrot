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


import os
from devparrot import capi
from devparrot.capi import Command
from devparrot.capi import constraints
from devparrot.core.session import bindings

@Command(
files = constraints.File(mode=(constraints.File.OPEN, constraints.File.NEW), help="a list of file to open")
)
def open(*files):
    """
    Open a existing or new file
    """
    for fileToOpen in files:
        open_a_file(fileToOpen)

def open_a_file(fileToOpen):
    if not fileToOpen: return False
    lineToGo = 1
    # if path doesn't exist and we have a line marker, lets go to that line
    if not os.path.exists(fileToOpen):
        parts = fileToOpen.split(':')
        if len(parts) == 2:
            fileToOpen = parts[0]
            try :
                lineToGo = int(parts[1])
            except ValueError:
                pass
    if capi.file_is_opened(fileToOpen):
        doc = capi.get_file(fileToOpen)
    else:
        from devparrot.core.errors import FileAccessError
        from devparrot.core.document import Document
        from devparrot.documents.fileDocSource import FileDocSource
        try:
            doc = Document(FileDocSource(fileToOpen))
            doc.load()
            capi.add_file(doc)
        except IOError:
            raise FileAccessError(doc.get_path())
    capi.set_currentDocument(doc)
    doc.goto_index("{}.0".format(lineToGo))


bindings["<Control-o>"] = "open\n"
