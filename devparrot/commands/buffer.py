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


from devparrot import capi
from devparrot.capi import Command, create_section
from devparrot.capi.constraints import Stream


def buffer(name, content):
    """Open a buffer and fill it with comment

A buffer is not attach to any file and can't be modified"""
    from devparrot.core.document import Document
    from devparrot.documents.bufferSource import BufferSource
    document = Document(BufferSource(name))
    capi.add_file(document)
    capi.set_currentDocument(document)
    model = document.get_model()

    def read_line():
        try:
            line = content.next()
            model.insert("insert", line)
            model.after_idle(read_line)
        except StopIteration:
            pass

    model.after_idle(read_line)

Command(content=Stream())(buffer, create_section("capi"))
