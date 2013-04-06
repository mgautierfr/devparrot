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
import logging
from devparrot.core import session

class StatusBar(Tkinter.Label, logging.Handler):
    def __init__(self, parent):
        Tkinter.Label.__init__(self, parent)
        logging.Handler.__init__(self)
        self.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
        session.userLogger.addHandler(self)

        self.currentLevel = 0
        self.callbackId = 0


    def flush(self):
        """overide logging.Handler.flush"""
        pass

    def clear(self):
        self.currentLevel = 0
        self["text"] = ""
        self.callbackId = 0

    def emit(self,record):
        """overide logging.Handler.emit"""
        print record.levelno
        if record.levelno >= self.currentLevel:
            self.currentLevel = record.levelno
            self["text"] = record.getMessage()
            if self.callbackId:
                self.after_cancel(self.callbackId)
            self.callbackId = self.after(5000, self.clear)
