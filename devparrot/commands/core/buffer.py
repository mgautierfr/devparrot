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
from devparrot.core.constraints import Keyword, Stream


@Command(
_section='core',
type=Keyword(('new','buffer'), default=lambda:'buffer'),
content=Stream()
)
def buffer(name, type, content):
    """Open a buffer and fill it with comment

A buffer is not attach to any file and can't be modified"""
    from devparrot.core import session
    from devparrot.core.document import Document
    from devparrot.documents.bufferSource import BufferSource
    from devparrot.documents.newDocSource import NewDocSource
    if type == 'buffer':
        document = Document(BufferSource(name))
    else:
        document = Document(NewDocSource(name))
    session.get_documentManager().add_file(document)
    session.commands.core.switch(document)
    model = document.get_model()

    def read_line():
        try:
            line = content.next()
            while line is not None:
                model.insert("insert", line)
                line = content.next()
            model.after(100, read_line)
        except StopIteration:
            pass

    model.after(100, read_line)

