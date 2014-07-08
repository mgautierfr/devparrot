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


from ui.documentView import DocumentView
from devparrot.views.textView import TextView
from devparrot.core import session

import utils.event
from utils.variable import Property, Variable, HasProperty
from devparrot.models.sourceBuffer import SourceBuffer


class Document(HasProperty):
    def get_title(self):
        return self.documentSource.title

    def get_longTitle(self):
        return self.documentSource.longTitle

    def get_mimetype(self):
        if self._mimetype.get() is None:
            return self.documentSource.mimetype
        return self._mimetype.get()

    def get_space_indent(self):
        if self._mimetype.get() is None:
            return session.config.space_indent
        return self._mimetype.get()

    title     = Property(fget=get_title, fset=None, fdel=None)
    longTitle = Property(fget=get_longTitle, fset=None, fdel=None)

    mimetype     = Property(fget=get_mimetype)
    space_indent = Property(fget=get_space_indent)



    def __init__(self, documentSource):
        self.documentSource = documentSource
        self.documentView = DocumentView(self)
        self.model = SourceBuffer(self)
        session.eventSystem.connect("modified", self.on_modified_changed)
        self.currentView = None
        self.set_view(TextView(self))

    def __eq__(self, other):
        if other == None:
            return False
        return self.documentSource == other.documentSource

    def set_view(self, view):
        view.set_model(self.model)
        self.documentView.set_view(view)
        self.currentView = view
        view.view.bind("<FocusIn>", self.on_focus_in_event, add="+")

    def get_currentView(self):
        return self.currentView

    def get_model(self):
        return self.model

    def has_a_path(self):
        return self.documentSource.has_path()

    def get_path(self):
        return self.documentSource.get_path()

    def set_path(self, documentSource):
        if (not "documentSource" in self.__dict__ or
            self.documentSource != documentSource):
            try:
                oldPath = self.documentSource.get_path()
            except AttributeError:
                oldPath = None
            self.documentSource = documentSource
            self.title_notify()
            self.longTitle_notify()
            session.eventSystem.event('pathChanged')(self, oldPath)

    def is_readonly(self):
        return self.documentSource.is_readonly()

    def load(self):
        with self.documentSource.get_content() as content:
            self.model.set_text(content)
        self.currentView.update_infos()
        session.eventSystem.event('textSet')(self)

    def write(self):
        self.documentSource.set_content(self.model.get_text())
        self.model.edit_modified(False)

    def on_modified_changed(self, model, modified):
        if model==self.model and not self.is_readonly():
            self.documentView.set_bold(modified)

    def on_focus_in_event(self, event):
        res = self.documentSource.need_reload()
        if res:
            import ui
            answer = ui.helper.ask_questionYesNo("File content changed",
                 "The content of file %s has changed.\nDo you want to reload it?"%self.title)
            if answer:
                self.load()
            self.documentSource.init_timestamp()

    def is_modified(self):
        return not self.is_readonly() and self.model.edit_modified()
        
    def search(self, backward, text):
        if self.model.search(backward, text):
            self.currentView.view.see("insert")
            return True
        return False

    def goto_index(self, index):
        self.currentView.view.sel_clear()
        self.currentView.view.mark_set("insert", str(index))
        self.currentView.view.see(str(index))


