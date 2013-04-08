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
from devparrot.core import session
from devparrot.core.command.commandCompleter import ControlerEntryCompletion

from pyparsing import printables, punc8bit, alphas8bit
validChars = set(printables+alphas8bit+punc8bit+" \t"+u'\u20ac')

class ControlerEntry(Tkinter.Text):
    def __init__(self, parent):
        Tkinter.Text.__init__(self, parent, height=1)
        self.toClean = False

        self.bind('<FocusIn>', self.on_get_focus)
        self.bind('<Key>', self.on_entry_event)

        self.completionSystem = ControlerEntryCompletion(self)

        self.pack(side=Tkinter.TOP, fill=Tkinter.X)

        self.bind('<Control-Return>', lambda e: "continue")

        bindtags = list(self.bindtags())
        bindtags.insert(1,"Command")
        bindtags = " ".join(bindtags)
        self.bindtags(bindtags)
    
    def on_entry_event(self, event):
        from devparrot.core import session
        from devparrot.core.errors import ContextError, InvalidError
        if event.keysym == 'Up':
            self.delete("1.0", "end")
            self.insert("end", session.commandLauncher.history.get_previous())
            self.completionSystem.update_completion()
            return
        if event.keysym == "Down":
            next = session.commandLauncher.history.get_next()
            if next:
                self.delete("1.0", "end")
                self.insert("end", session.commandLauncher.history.get_next())
                self.completionSystem.update_completion()
            else:
                self.completionSystem.start_completion()
            return
        if event.keysym == 'Return':
            self.completionSystem.stop_completion()
            text = self.get("1.0", "end")
            try:
                try:
                    session.commandLauncher.run_command(text[:-1])
                    session.userLogger.info(text[:-1])
                    self.toClean = True
                except ContextError as err:
                    session.userLogger.error(err)
                    self.toClean = True
                except InvalidError as err:
                    session.userLogger.invalid(err)
                    self.toClean = False
                if session.get_currentDocument():
                    session.get_currentDocument().get_currentView().focus()
            except Exception as err:
                self.userLogger.error(err)
            finally:
                return "break"
        if event.keysym == 'Escape':
            self.completionSystem.stop_completion()
            if session.get_currentDocument():
                session.get_currentDocument().get_currentView().focus()
            return
        if event.keysym == 'BackSpace':
            try:
                self.delete( 'sel.first', 'sel.last' )
                self.tag_remove( 'sel', '1.0', 'end' )
                self.mark_unset( 'sel.first', 'sel.last' )
            except Tkinter.TclError:
                self.delete( 'insert -1 chars', 'insert' )
            self.completionSystem.update_completion()
            return "break"
        char = event.char.decode('utf8')
        if char in validChars:
            self.tag_remove( 'sel', '1.0', 'end' )
            self.mark_unset( 'sel.first', 'sel.last' )
            self.insert( 'insert', char)
            self.completionSystem.update_completion(True)
            return "break"
        
    def on_get_focus(self, event):
        if self.toClean:
            self.toClean = False
            self.delete("1.0",'end')



