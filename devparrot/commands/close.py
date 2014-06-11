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
from devparrot.core.command import Command, Alias
from devparrot.core.session import bindings
from devparrot.capi.constraints import OpenDocument
from devparrot.core.errors import UserCancel
from devparrot.core import session


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
            session.commands.core.save(document)
        else:
            answer = capi.ui.helper.ask_filenameSave()
            if not answer:
                raise UserCancel()
            session.commands.core.save(document, answer)
    for document in documents:
        session.commands.core.close(document)

@Alias()
def closeall():
    """close all opened documents"""
    return "close %%all_document"

bindings["<Control-w>"] = "close\n"
