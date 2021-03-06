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


import tkinter
from devparrot.core import session
from functools import partial
from devparrot.core.errors import *
from devparrot.core.configLoader import ReadOnlyOption
   

class Menu(tkinter.Menu):
    def __init__(self, parent, entries=None, **kw):
        tkinter.Menu.__init__(self, parent, **kw)
        self.entries = []
        if entries is None:
            entries = []
        [self.append(v) for v in entries]

    def create_entry(self, where, value):
        if where >= len(self.children):
            tkadd = partial(tkinter.Menu.add, self)
        else:
            tkadd = partial(tkinter.Menu.insert, self, where)
        if value == "---":
            tkadd('separator')
            value = ("---", "---")
        else:
            name, what = value
            if isinstance(what, list):
                subMenu = Menu(self, what)
                value = (name, subMenu)
                tkadd('cascade', label=name, menu=subMenu)
            elif isinstance(what, Menu):
                tkadd('cascade', label=name, menu=what)
            else:
                entry = MenuEntry(what)
                value = (name, entry)
                tkadd('command', label=name, command=entry)
        return value

    def __contains__(self, name):
        for n, _ in self.entries:
            if name == n:
                return True
        return False

    def append(self, value):
        value = self.create_entry(len(self), value)
        self.entries.append(value)
        return value

    def __len__(self):
        return len(self.entries)

    def __getitem__(self, key):
        try:
            return self.entries[key]
        except TypeError:
            for n, e in self.entries:
                if n == key:
                    return e
        raise KeyError("%r is not a valid entry in the menu"%key)

    def __setitem__(self, key, value):
        value = self.create_entry(key, value)
        self.entries[key] = value
        return value

    def __delitem__(self, key):
        del self.entries[key]
        self.delete(key)

    def __iter__(self):
        return iter(self.entries)

class MenuEntry:
    def __init__(self, cmd):
        self.set_command(cmd)

    def set_command(self, command):
        commands = command.split('\n')
        self.commands = commands[:-1]
        self.leftText = commands[-1]

    def __call__(self, *args, **kwords):
        for cmd in self.commands:
            ret = session.commandLauncher.run_command_nofail(cmd)
            if not ret:
                return
        if self.leftText:
            session.window.entry.delete("1.0", "end")
            session.window.entry.insert("1.0", self.leftText)
            session.window.entry.toClean = False
            session.window.entry.focus()
            session.window.entry.mark_set("index", "end")

class MenuBar(Menu):
    def __init__(self):
        Menu.__init__(self, parent=None)
        self.create_menu()
        dict.__setitem__(session.config.options, 'menuBar', ReadOnlyOption('menuBar', session.config, session.config, str, self))

    def create_menu(self):
        [self.append(value) for value in session.config.get('menuBar')]


class PopupMenu(Menu):
    def __init__(self):
        Menu.__init__(self, parent=None)
        self.config(postcommand=self.postCommand)
        self.create_menu()
        dict.__setitem__(session.config.options, 'popupMenu', ReadOnlyOption('popupMenu', session.config, session.config, str, self))

    def create_menu(self):
        [self.append(value) for value in session.config.get('popupMenu')]

    def postCommand(self):
        try:
            self.clipboard_get()
            self.entryconfigure('Paste', state="normal")
        except TclError:
            self.entryconfigure('Paste', state="disable")

        if session.get_currentDocument().is_readonly():
            self.entryconfigure("Paste", state="disable")
            self.entryconfigure("Cut", state="disable")

