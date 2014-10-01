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


import ttk, Tkinter
from xdg import Mime
from viewContainer import NotebookContainer, ContainerChild
from devparrot.core import mimemapper
from pygments.lexers import get_all_lexers, get_lexer_for_mimetype
from pygments.util import ClassNotFound

from devparrot.core import session

def get_valid_lexer_names():
    for name, aliases, filetype, mimetypes in get_all_lexers():
        if mimetypes:
            yield name

class DocumentView(ContainerChild, ttk.Frame):
    def __init__(self, document):
        ContainerChild.__init__(self)
        ttk.Frame.__init__(self, session.get_globalContainer(), padding=0, relief="flat", borderwidth=0)
        self.document = document
        self.currentView = None
        
        import tkFont

        self.header = ttk.Frame(self)
        self.header.pack(fill='x')

        self.label = ttk.Label(self.header)
        self.label.font = tkFont.Font(font="TkDefaultFont")
        self.label.documentView = self
        self.label['text'] = document.longTitle
        self.label['font'] = self.label.font
        self.label.pack(side='left', expand=True, fill="x")

        separator = ttk.Separator(self.header, orient="vertical")
        separator.pack(side='left', fill='y')

        self.mimeVar = Tkinter.StringVar()
        self.mimeOption = ttk.Combobox(self.header, textvar=self.mimeVar)
        self.mimeOption.set(mimemapper.mimeMap.get(str(document.get_mimetype()), "UNKNOWN"))
        self.mimeOption['values'] = sorted(mimemapper.mimeMap.values())
        self.mimeVar.trace('w', self.on_mimeChange)
        self.mimeOption.pack(side='right', expand=False, fill="none")

        document.longTitle_register(self.on_title_changed)

        self.bind('<FocusIn>', self.on_focus)
        
    def set_view(self, child):
        child.uiContainer.pack(in_=self, expand=True, fill=ttk.Tkinter.BOTH)
        self.currentView = child
        child.view.bind('<FocusIn>', self.on_focus_child)

    def on_mimeChange(self, *args):
        mimetype = next(k for k,v in mimemapper.mimeMap.items() if v==self.mimeVar.get())
        self.document.mimetype = mimetype
    
    def lift(self):
        ttk.Frame.lift(self, self.parentContainer)
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
        self.parentContainer.set_as_current()
        
    def dnd_end(self, target, event):
        pass	
    
            

