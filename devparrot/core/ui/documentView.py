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


import tkinter, tkinter.ttk, tkinter.font
from xdg import Mime
from .viewContainer import NotebookContainer, ContainerChild
from devparrot.core import mimemapper

from devparrot.core import session

class DocumentView(tkinter.ttk.Frame, ContainerChild):
    def __init__(self, document):
        ContainerChild.__init__(self)
        tkinter.ttk.Frame.__init__(self, session.get_globalContainer(), padding=0, relief="flat", borderwidth=0)
        self.document = document
        self.currentView = None

        self.header = tkinter.ttk.Frame(self)
        self.header.pack(fill='x')

        self.label = tkinter.ttk.Label(self.header)
        self.label.font = tkinter.font.Font(font="TkDefaultFont")
        self.label.documentView = self
        self.label['text'] = document.longTitle
        self.label['font'] = self.label.font
        self.label.pack(side='left', expand=True, fill="x")

        separator = tkinter.ttk.Separator(self.header, orient="vertical")
        separator.pack(side='left', fill='y')

        self.mimeVar = tkinter.StringVar()
        self.mimeOption = tkinter.ttk.Combobox(self.header, textvar=self.mimeVar, state="readonly")
        self.mimeOption.set(mimemapper.mimeMap.get(str(document.get_mimetype()), "Text only"))
        self.mimeOption['values'] = sorted(set(mimemapper.mimeMap.values()))
        self.mimeChangeHandle = self.mimeVar.trace('w', self.on_mimeChange)
        self.mimeOption.pack(side='right', expand=False, fill="none")
        self._ownChange = False

        document.longTitle_register(self.on_title_changed)
        document.mimetype_register(self.on_mimetype_changed)

        self.bind('<FocusIn>', self.on_focus)

    def destroy(self):
        self.mimeVar.trace_vdelete('w', self.mimeChangeHandle)
        tkinter.ttk.Frame.destroy(self)
        self.header.destroy()
        self.label.destroy()
        self.mimeOption.destroy()
        self.header = self.label = self.mimeOption = self.currentView = self.document = None
        self.mimeChangeHandle = None
        
    def set_view(self, child):
        child.uiContainer.pack(in_=self, expand=True, fill=tkinter.BOTH)
        self.currentView = child
        child.view.bind('<FocusIn>', self.on_focus_child)

    def on_mimeChange(self, *args):
        if self._ownChange:
            return
        mimetype = next(k for k,v in mimemapper.mimeMap.items() if v==self.mimeVar.get())
        self.document.mimetype = mimetype

    def on_mimetype_changed(self, var, old):
        self._ownChange = True
        self.mimeOption.set(mimemapper.mimeMap[str(self.document.mimetype)])
        self._ownChange = False
    
    def lift(self):
        tkinter.ttk.Frame.lift(self, self.parentContainer)
        if self.currentView != None: 
            self.currentView.lift(self)
    
    def on_title_changed(self, newtitle, oldTitle):
        self.label['text'] = self.document.longTitle

    def set_bold(self, bold):
        self.label.font['weight'] = "bold" if bold else "normal"

    def is_displayed(self):
        return self.parentContainer != None
        
    def on_focus(self, event):
        self.currentView.focus()

    def on_focus_child(self, event):
        if self.parentContainer:
            self.parentContainer.set_as_current()
        
    def dnd_end(self, target, event):
        pass	
    
            

