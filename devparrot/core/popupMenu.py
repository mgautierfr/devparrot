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


import Tkinter
import session
from devparrot.core.errors import *


class Menu(Tkinter.Menu):
    def __init__(self):
        Tkinter.Menu.__init__(self)
        self.sections = []
        self.config(postcommand=self.postCommand)
        self.add_section(EditSection(self))
        self.createMenu()
    
    def add_section(self, section):
        self.sections.append(section)
    
    def createMenu(self):
        for section in self.sections:
            section.createMenu()
    
    def postCommand(self):
        for section in self.sections:
            section.postCommand()
        
class EditSection:
    def __init__(self, menu):
        self.menu = menu
    
    def createMenu(self):
        self.menu.add_command(label='Undo', command=lambda:session.commandLauncher.run_command_nofail('undo'))
        self.menu.add_command(label='Redo', command=lambda:session.commandLauncher.run_command_nofail('redo'))
        self.menu.add_separator()
        self.menu.add_command(label='Copy',  command=lambda:session.commandLauncher.run_command_nofail('copy'))
        self.menu.add_command(label='Cut',   command=lambda:session.commandLauncher.run_command_nofail('cut'))
        self.menu.add_command(label='Paste', command=lambda:session.commandLauncher.run_command_nofail('paste'))
    
    def postCommand(self):
        try:
            self.menu.clipboard_get()
            self.menu.entryconfigure('Paste', state="normal")
        except TclError:
            self.menu.entryconfigure('Paste', state="disable")

        import session
        if session.get_currentDocument().get_currentView().view.sel_isSelection():
            self.menu.entryconfigure('Cut', state="normal")
            self.menu.entryconfigure('Copy', state="normal")
        else:
            self.menu.entryconfigure('Cut', state="disable")
            self.menu.entryconfigure('Copy', state="disable")

        if session.get_currentDocument().is_readonly():
            self.menu.entryconfigure("Paste", state="disable")
            self.menu.entryconfigure("Cut", state="disable")
