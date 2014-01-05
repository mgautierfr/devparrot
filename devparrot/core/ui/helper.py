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


class HelperContainer(object):
    def __init__(self, panned, where):
        self.panned = panned
        self.where = where
        self.notebook = None
        self.helpers = []

    def add_helper(self, helper, name, notebookForced):
        import ttk
        if self.notebook is None:
            if not notebookForced and not self.helpers:
                self.panned.insert(self.where, helper)
            else:
                self.notebook = ttk.Notebook(self.panned)
                try:
                    oldHelper, oldName = self.helpers[0]
                    self.panned.forget(oldHelper)
                    self.notebook.insert('end', oldHelper, text=oldName)
                except IndexError:
                    pass
                self.panned.insert(self.where, self.notebook)

        if self.notebook:
            self.notebook.insert('end', helper, text=name)
            self.notebook.select(helper)
        self.helpers.append((helper, name))

    def remove_helper(self, widget):
        index = (i for i, data in enumerate(self.helpers) if data[0] == widget).next()
        self.notebook.forget(widget)
        del self.helpers[index]
        if not self.helpers:
            self.panned.forget(self.notebook)
            self.notebook.destroy()
            self.notebook = None


class HelperManager(object):
    def __init__(self, window):
        self.window = window
        self.containers = {'left'  : HelperContainer(window.hpaned, 0),
                           'right' : HelperContainer(window.hpaned, 'end'),
                           'top'   : HelperContainer(window.vpaned, 0),
                           'bottom': HelperContainer(window.vpaned, 'end')}

    def add_helper(self, widget, name, pos, notebookForced = False):
        helperContainer = self.containers[pos]
        helperContainer.add_helper(widget, name, notebookForced)

    def remove_helper(self, widget, pos):
        helperContainer = self.containers[pos]
        helperContainer.remove_helper(widget)

def ask_questionYesNo(title, message):
    import tkMessageBox
    return tkMessageBox.askyesno(title, message)

def ask_questionYesNoCancel(title, message):
    import tkMessageBox
    return tkMessageBox.askyesnocancel(title, message)

def ask_filenameSave(*args, **kwords):
    import tkFileDialog
    response = tkFileDialog.asksaveasfilename(title="Save a file", *args, **kwords)
    return response

def ask_filenameOpen(*args, **kwords):
    import tkFileDialog
    response = tkFileDialog.askopenfilename(title="Open a file", *args, **kwords)
    return response


