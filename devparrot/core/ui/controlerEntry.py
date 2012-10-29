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

class ControlerEntry(Tkinter.Text):
    def __init__(self, parent):
        Tkinter.Text.__init__(self, parent, height=1)
        self.toClean = False
        
        self.bind('<FocusIn>', self.on_get_focus)
        self.bind('<Key>', self.on_entry_event)

        self.completionSystem = completion.CompletionSystem(self)
        

        self.pack(side=Tkinter.TOP, fill=Tkinter.X)

        self.bind('<Control-Return>', lambda e: "continue")
        
        self.bind("<<Modified>>", self.on_textChanged)

        bindtags = list(self.bindtags())
        bindtags.insert(1,"Command")
        bindtags = " ".join(bindtags)
        self.bindtags(bindtags)
    
    def on_entry_event(self, event):
        from devparrot.core import session
        if event.keysym == 'Up':
            self.delete("1.0", "end")
            self.insert("end", session.commandLauncher.controler.history.get_previous())
        if event.keysym == "Down":
            next = session.commandLauncher.controler.history.get_next()
            if next:
                self.delete("1.0", "end")
                self.insert("end", session.commandLauncher.controler.history.get_next())
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
            print text
            ret = session.commandLauncher.run_command(text)
            if ret is None:
                self.configure(background=session.config.color.notFoundColor)
            elif ret:
                self.configure(background=session.config.color.okColor)
                self.toClean = True
            else:
                self.configure(background=session.config.color.errorColor)
            if session.get_currentDocument():
                session.get_currentDocument().get_currentView().focus()
            return "break"
        if event.keysym == 'Escape':
            self.completionSystem.stop_completion()
            if session.get_currentDocument():
                session.get_currentDocument().get_currentView().focus()
            return

    def on_textChanged(self, *args):
        startIndex, completions = session.commandLauncher.get_completions(self.get("1.0", "insert"))
        self.completionSystem.update_completion("1.%d"%startIndex, completions)
        self.edit_modified(False)
        
    def on_get_focus(self, event):
        if self.toClean:
            self.toClean = False
            self.configure(background="white")
            self.delete("1.0",'end')
