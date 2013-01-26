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

import Tkinter
from devparrot.core import session, completion

from pyparsing import printables, punc8bit, alphas8bit
validChars = set(printables+alphas8bit+punc8bit+" \t"+u'\u20ac')

class ControlerEntry(Tkinter.Text):
    def __init__(self, parent):
        Tkinter.Text.__init__(self, parent, height=1)
        self.toClean = False
        
        self.bind('<FocusIn>', self.on_get_focus)
        self.bind('<Key>', self.on_entry_event)

        self.completionSystem = completion.CompletionSystem(self)
        

        self.pack(side=Tkinter.TOP, fill=Tkinter.X)

        self.bind('<Control-Return>', lambda e: "continue")
        
        bindtags = list(self.bindtags())
        bindtags.insert(1,"Command")
        bindtags = " ".join(bindtags)
        self.bindtags(bindtags)

        self.completionProtected = False
    
    def on_entry_event(self, event):
        from devparrot.core import session
        if event.keysym == 'Up':
            self.delete("1.0", "end")
            self.insert("end", session.commandLauncher.history.get_previous())
            self.update_completion()
            return
        if event.keysym == "Down":
            next = session.commandLauncher.history.get_next()
            if next:
                self.delete("1.0", "end")
                self.insert("end", session.commandLauncher.history.get_next())
                self.update_completion()
            else:
                self.completionSystem.start_completion()
            return
        if event.keysym == 'Tab':
            self.completionSystem.complete(self.completionSystem.get_common())
            self.completionSystem.start_completion()
            return "break"
        if event.keysym == 'Return':
            self.completionSystem.stop_completion()
            text = self.get("1.0", "end")
            try:
                ret = session.commandLauncher.run_command(text[:-1])
            except Exception:
                self.configure(background=session.config.get("color.errorColor"))
            else:
                self.configure(background=session.config.get("color.okColor"))
                self.toClean = True
            if session.get_currentDocument():
                session.get_currentDocument().get_currentView().focus()
            return "break"
        if event.keysym == 'Escape':
            self.completionSystem.stop_completion()
            if session.get_currentDocument():
                session.get_currentDocument().get_currentView().focus()
            return
        char = event.char.decode('utf8')
        if char in validChars:
            self.insert( 'insert', char)
            self.update_completion(True)
            return "break"

    def update_completion(self, autoCommon = False):
        text = self.get('1.0', 'insert')
        startIndex, completions = session.commandLauncher.get_completions(text)
        if startIndex is None:
            startIndex = len(text)
        self.completionSystem.update_completion("1.%d"%startIndex, completions)
        common = self.completionSystem.get_common()
        if autoCommon and not text.endswith(common):
            self.completionSystem.complete(common)
            

    def replace(self, startIndex, endIndex, text, *args):
        self.tk.call((self._w, 'replace', startIndex, endIndex, text) + args)
        self.mark_set("insert", startIndex +"+%dc"%len(text))
        self.update_completion(True)
        
    def on_get_focus(self, event):
        if self.toClean:
            self.toClean = False
            self.configure(background="white")
            self.delete("1.0",'end')
