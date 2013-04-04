#    This file is part of DevParrot.
#
#    Author: Matthieu Gautier <matthieu.gautier@mgautier.fr>
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
#    Copyright 2011 Matthieu Gautier


import sys
from devparrot.core import session

class ModuleWrapper(object):
    def __init__(self, module):
        self.__dict__['module'] = module
    
    def __getattr__(self, name):
        try:
            return getattr(self.module, name)
        except AttributeError:
            return self.module.__getattr__(name)
    
    def __setattr__(self, name, value):
        return self.module.__setattr__(name, value)
            
class DocumentWrapper(object):
    def __init__(self):
        pass
        
    def __len__(self):
        from devparrot.core import session
        return session.get_documentManager().get_nbDocuments()
    
    def __getitem__(self, key):
        from devparrot.core import session
        return session.get_documentManager().get_nthFile(key)


def __getattr__(name):
    if name == 'currentDocument':
        return session.get_currentDocument()
    if name == 'currentContainer':
        return session.get_currentContainer()
    if name == 'bind':
        from devparrot.core.command import binder
        return binder
    raise AttributeError

def __setattr__(name, value):
    if name == 'currentDocument':
        if value == None:
            session.get_currentContainer().set_documentView(None)
        elif value.documentView.is_displayed():
            value.documentView.parentContainer.select(value.documentView)
            value.documentView.focus()
        else:
            session.get_currentContainer().set_documentView(value.documentView)
            value.documentView.focus()

        return
    raise AttributeError

def add_file(document):
    from devparrot.core import session
    return session.get_documentManager().add_file(document)

def file_is_opened(filePath):
    from devparrot.core import session
    return session.get_documentManager().has_file(filePath)

def get_file(filePath):
    from devparrot.core import session
    return session.get_documentManager().get_file(filePath)
    
def get_nth_file(index):
    from devparrot.core import session
    return session.get_documentManager().get_nthFile(index)

def close_document(document):
    from devparrot.core import session
    if document.check_for_save():
        save_document(document, document.get_path())
    if document.documentView.is_displayed():
        parentContainer = document.documentView.get_parentContainer()
        parentContainer.detach_child(document.documentView)
        if parentContainer.get_nbChildren() == 0:
            unsplit(parentContainer)
    return session.get_documentManager().del_file(document)

def open_file(filePath):
    if file_is_opened(filePath):
        return get_file(filePath)
    from devparrot.core import document
    from devparrot import documents
    doc = document.Document(documents.fileDocSource.FileDocSource(filePath))
    add_file(doc)
    doc.load()
    return doc

def save_document(document, fileToSave):
    from devparrot.core import session
    if document.has_a_path() and document.get_path() == fileToSave:
        return document.write()

    # we've ask to change the path
    if file_is_opened(fileToSave):
        #The document is already opened.
        #do nothing (should warn or save/close/reopen)
        return False

    from devparrot.documents.fileDocSource import FileDocSource
    document.set_path(FileDocSource(fileToSave))
    session.get_documentManager().del_file(document)
    session.get_documentManager().add_file(document)
    return document.write()

def quit():
    from devparrot.core import ui
    def destroy():
        ui.window.destroy()	
    ui.window.after_idle(destroy)
    
def split(vertical, first=True):
    from devparrot.core.ui import viewContainer
    return viewContainer.split(session.get_currentContainer().get_documentView(), vertical, first)

def unsplit(container=None):
    from devparrot.core.ui import viewContainer
    if not container:
        container = session.get_currentContainer()
    return viewContainer.unsplit(container)

sys.modules[__name__] = ModuleWrapper(sys.modules[__name__])
documents = DocumentWrapper()
