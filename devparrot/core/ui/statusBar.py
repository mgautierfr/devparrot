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


import Tkinter, ttk
import logging
from devparrot.core import session, userLogging

class StatusBar(Tkinter.Frame, logging.Handler):
    def __init__(self, parent):
        Tkinter.Frame.__init__(self, parent)
        logging.Handler.__init__(self)
        self.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
        self['relief'] = 'sunken'
        session.userLogger.addHandler(self)

        self.label = Tkinter.Label(self)
        self.label.pack(side='left', fill=Tkinter.BOTH, expand=True)
        self.defaultColor = self['background']
        self.label['anchor'] = 'nw'

        separator = ttk.Separator(self, orient="vertical")
        separator.pack(side='left', fill='y')

        self.insertLabel = ttk.Label(self)
        self.insertLabel.pack(side='right', expand=False, fill="none")
        session.eventSystem.connect('mark_set', self.on_mark_set)

        self.currentLevel = 0
        self.callbackId = 0


    def flush(self):
        """overide logging.Handler.flush"""
        pass

    def clear(self):
        self.currentLevel = 0
        self.label['text'] = ""
        self.label['background'] = self.defaultColor
        self.callbackId = 0

    def emit(self,record):
        """overide logging.Handler.emit"""
        if record.levelno >= self.currentLevel:
            self.currentLevel = record.levelno
            self.label['text'] = record.getMessage()
            if self.currentLevel == userLogging.INFO:
                self.label['background'] = session.config.get('ok_color')
            if self.currentLevel == userLogging.ERROR:
                self.label['background'] = session.config.get('error_color')
            if self.currentLevel == userLogging.INVALID:
                self.label['background'] = session.config.get('invalid_color')
            if self.callbackId:
                self.after_cancel(self.callbackId)
            self.callbackId = self.after(5000, self.clear)

    def on_mark_set(self, model, name, index):
        if name == "insert":
            if model.sel_isSelection():
                self.insertLabel['text'] = "[%s:%s]"%(model.index("sel.first"), model.index("sel.last"))
            else:
                self.insertLabel['text'] = str(model.index("insert"))
