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


from devparrot.capi import Command
from devparrot.core.session import bindings
from devparrot.capi.constraints import OpenDocument
from devparrot import capi


@Command(
    documents = OpenDocument(default=capi.get_currentDocument, help="documents to close")
)
def close(*documents):
    "close one or several documents"
    for document in documents:
        capi.close_document(document)

@Command()
def closeall():
    """close all opened documents"""
    while len(capi.documents):
        capi.close_document(capi.get_nth_file(0))

bindings["<Control-w>"] = "close\n"
