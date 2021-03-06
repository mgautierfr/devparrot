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


import tkinter, tkinter.ttk
try:
    from PIL.ImageTk import PhotoImage
    from PIL import Image
except ImportError:
    PhotoImage = None
from os.path import join

from . import menu
from . import controlerEntry
from . import statusBar

from pkg_resources import resource_stream

def quit():
    from devparrot.core import session
    session.commandLauncher.run_command_nofail("quit")

class MainWindow(tkinter.Tk):
    def __init__(self):
        from devparrot.core import session
        tkinter.Tk.__init__(self, className='Devparrot')
        geom = self.wm_geometry()
        w = int(geom.split('+')[0].split('x')[0])
        try:
            w = session.config.get('window_width')
        except AttributeError:
            pass
        h = int(geom.split('+')[0].split('x')[1])
        try:
            h = session.config.get('window_height')
        except AttributeError:
            pass
        x = int(geom.split('+')[1])
        try:
            x = session.config.get('window_x')
        except AttributeError:
            pass
        y = int(geom.split('+')[2])
        try:
            y = session.config.get('window_y')
        except AttributeError:
            pass
        self.wm_geometry("%dx%d+%d+%d"%(w, h, x, y))
        self.wm_title("devparrot")

        self.protocol('WM_DELETE_WINDOW', quit)

        if PhotoImage:
            resource = resource_stream(__name__, 'resources/icon48.png')
            img = PhotoImage(Image.open(resource))
            self.wm_iconphoto(False, img)

        self._vbox = tkinter.Frame(self)
        self._vbox.pack(expand=True, fill=tkinter.BOTH)
        
        self.entry = controlerEntry.ControlerEntry(self._vbox)

        self.hpaned = tkinter.ttk.PanedWindow(self._vbox, orient=tkinter.HORIZONTAL)
        self.hpaned.pack(expand=True, fill=tkinter.BOTH)

        self.vpaned = tkinter.ttk.PanedWindow(self.hpaned, orient=tkinter.VERTICAL)

        self.globalContainer = tkinter.ttk.Frame(self.vpaned, borderwidth=1, padding=0, relief="ridge")
        self.vpaned.add(self.globalContainer, weigh=1)

        self.hpaned.add(self.vpaned, weigh=1)

        self.statusBar = statusBar.StatusBar(self._vbox)

        self.popupMenu = menu.PopupMenu()
        self.menuBar = menu.MenuBar()
        self['menu'] = self.menuBar

        self.bind_class("devparrot", "<Control-Return>", self.focus_and_break)
        self.bind_class("devparrot", '<ButtonRelease>', lambda e: self.popupMenu.unpost() )
        self.bind_class("devparrot", '<Configure>', lambda e: self.popupMenu.unpost() )
        bindtags = list(self.bindtags())
        bindtags.insert(1,"devparrot")
        bindtags = " ".join(bindtags)
        self.bindtags(bindtags)

    def report_callback_exception(self, *args):
        from devparrot.core import session
        import traceback, tkinter.messagebox
        err = ''.join(traceback.format_exception(*args))
        session.logger.error(err)
        tkinter.messagebox.showerror('Exception', "An exception occurs\nPlease report to devparrot team", detail=err)
    
    def get_globalContainer(self):
        return self.globalContainer
        
    def focus_and_break(self, event):
        self.entry.focus()
        return "break"


