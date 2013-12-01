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
from devparrot.capi import Command
from devparrot.core.session import bindings
from devparrot.capi.constraints import OpenDocument
from devparrot.core.errors import UserCancel


def ask_save_question(document):
    answer = capi.ui.helper.ask_questionYesNoCancel("Save document ?", "Document %(documentName)s is changed.\n Do you want to save it?"%{'documentName':document.title})
    if answer is None:
        raise UserCancel()
    return answer

@Command(
    documents = OpenDocument(default=capi.get_currentDocument, help="documents to close")
)
def close(*documents):
    "close one or several documents"
    documents_modified = [d for d in documents if d.is_modified()]
    documents_must_save = [d for d in documents_modified if ask_save_question(d)]
    for document in documents_must_save:
        if document.has_a_path():
            capi.save_document(document, document.get_path())
        else:
            answer = capi.ui.helper.ask_filenameSave()
            if not answer:
                raise UserCancel()
            capi.save_document(document, answer)
    for document in documents:
        capi.close_document(document)

@Command()
def closeall():
    """close all opened documents"""
    close(*capi.documents)

bindings["<Control-w>"] = "close\n"
