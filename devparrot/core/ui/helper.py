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

from devparrot.core.errors import *


class HelperContainer:
    def __init__(self, panned, where):
        self.panned = panned
        self.where = where
        self.notebook = None
        self.helpers = []

    def add_helper(self, helper, name, notebookForced, middleClickCallback):
        import tkinter.ttk
        if self.notebook is None:
            if not notebookForced and not self.helpers:
                self.panned.insert(self.where, helper, weigh=0)
            else:
                self.notebook = tkinter.ttk.Notebook(self.panned, height=150)
                self.notebook.bind("<Button-2>", self.on_middleClickButton)
                try:
                    oldHelper, oldName, _ = self.helpers[0]
                    self.panned.forget(oldHelper)
                    self.notebook.insert('end', oldHelper, text=oldName)
                except IndexError:
                    pass
                self.panned.insert(self.where, self.notebook, weigh=0)

        if self.notebook:
            self.notebook.insert('end', helper, text=name)
            self.notebook.select(helper)
        self.helpers.append((helper, name, middleClickCallback))

    def remove_helper(self, widget):
        index = next((i for i, data in enumerate(self.helpers) if data[0] == widget))
        del self.helpers[index]
        if self.notebook:
            self.notebook.forget(widget)
            if not self.helpers:
                self.panned.forget(self.notebook)
                self.notebook.destroy()
                self.notebook = None
        else:
            self.panned.forget(widget)

    def on_middleClickButton(self, event):
        try:
            child = self.notebook.index("@%d,%d" % (event.x, event.y))
        except TclError:
            return
        try:
            _, _, callback = self.helpers[child]
            callback()
        except TypeError:
            # child is a string if user doesn't click on a signet
            pass


class HelperManager:
    def __init__(self, window):
        self.window = window
        self.containers = {'left'  : HelperContainer(window.hpaned, 0),
                           'right' : HelperContainer(window.hpaned, 'end'),
                           'top'   : HelperContainer(window.vpaned, 0),
                           'bottom': HelperContainer(window.vpaned, 'end')}

    def add_helper(self, widget, name, pos, notebookForced = False, middleClickCallback=None):
        helperContainer = self.containers[pos]
        helperContainer.add_helper(widget, name, notebookForced, middleClickCallback)

    def remove_helper(self, widget, pos):
        helperContainer = self.containers[pos]
        helperContainer.remove_helper(widget)

def ask_questionYesNo(title, message):
    import tkinter.messagebox
    return tkinter.messagebox.askyesno(title, message)

def ask_questionYesNoCancel(title, message):
    import tkinter.messagebox
    return tkinter.messagebox.askyesnocancel(title, message)

def ask_filenameSave(*args, **kwords):
    import tkinter.filedialog
    response = tkinter.filedialog.asksaveasfilename(title="Save a file", *args, **kwords)
    return response

def ask_filenameOpen(*args, **kwords):
    import tkinter.filedialog
    response = tkinter.filedialog.askopenfilename(title="Open a file", *args, **kwords)
    return response

def ask_directory(*args, **kwords):
    import tkinter.filedialog
    response = tkinter.filedialog.askdirectory(title="Choose a directory", *args, **kwords)
    return response

