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


import tkinter, tkinter.ttk

from devparrot.core import session
from devparrot.core.modules import BaseModule

class DocumentListView(tkinter.ttk.Treeview):
    class PseudoList:
        def __init__(self, ttkTreeView):
            self.view = ttkTreeView

        def __len__(self):
            return len(self.view.get_children(''))

        def __getitem__(self, key):
            return self.view.get_children('')[key]

        def __delitem__(self, key):
            self.view.detach(self.__getitem__(key))

        def sort(self):
            sorted_ = sorted(self)
            for i in range(len(self)):
                del self[0]
            for i,p in enumerate(sorted_):
                self.view.reattach(p, '', i)
                self.view.item(p, text="%d"%i)


    def __init__(self,parent):
        tkinter.ttk.Treeview.__init__(self,parent)
        self['columns'] = ('name')
        self.column('#0', width=30, stretch=False)
        self.heading('#0', text="id")
        self.heading('name', text="document")
        self['selectmode'] =(tkinter.BROWSE)
        self.bind('<Double-Button-1>', self.on_double_click)
        bindtags = list(self.bindtags())
        bindtags.insert(1,"devparrot")
        bindtags = " ".join(bindtags)
        self.bindtags(bindtags)
        nb_doc = session.get_documentManager().get_nbDocuments()
        [self._add_document(session.get_documentManager().get_nthFile(i)) for i in xrange(nb_doc)]
        self.sort()

    def _add_document(self, document):
        tkinter.ttk.Treeview.insert(self, '', 'end', iid=document.get_path(), text="0", values=('"%s"'%document.title))

    def on_double_click(self, event):
        from devparrot.core import session
        selection = self.selection()
        if selection:
            document = session.get_documentManager().get_file(selection[0])
            if document.documentView.is_displayed():
                document.documentView.parentContainer.select(document.documentView)
            else:
                session.get_currentContainer().set_documentView(document.documentView)
            document.documentView.focus()

    def sort(self):
        DocumentListView.PseudoList(self).sort()


class DocumentList(BaseModule):
    def __init__(self, name):
        BaseModule.__init__(self, name)
        self.documentListView = None

    def activate(self):
        self.documentListView = DocumentListView(session.window)
        session.helperManager.add_helper(self.documentListView, "documentList", 'left')

    def deactivate(self):
        pass

    def on_documentAdded(self, document):
        self.documentListView._add_document(document)
        self.documentListView.sort()

    def on_documentDeleted(self, document):
        self.documentListView.delete(document.get_path())
        self.documentListView.sort()

    def on_pathChanged(self, document, oldPath):
        if oldPath:
            self.documentListView.delete(oldPath)
        self.documentListView._add_document(document)
        self.documentListView.sort()

