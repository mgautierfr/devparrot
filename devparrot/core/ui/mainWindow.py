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


import ttk
try:
    from PIL.ImageTk import PhotoImage
    from PIL import Image
except ImportError:
    PhotoImage = None
from os.path import join

import menu
import controlerEntry
import statusBar

from pkg_resources import Requirement, resource_stream

def quit():
    from devparrot.core import session
    session.commandLauncher.run_command_nofail("quit")

class MainWindow(ttk.Tkinter.Tk):
    def __init__(self):
        from devparrot.core import session
        ttk.Tkinter.Tk.__init__(self, className='Devparrot')
        geom = self.wm_geometry()
        w = geom.split('+')[0].split('x')[0]
        try:
            w = session.config.get('window_width')
        except AttributeError:
            pass
        h = geom.split('+')[0].split('x')[1]
        try:
            h = session.config.get('window_height')
        except AttributeError:
            pass
        x = geom.split('+')[1]
        try:
            x = session.config.get('window_x')
        except AttributeError:
            pass
        y = geom.split('+')[2]
        try:
            y = session.config.get('window_y')
        except AttributeError:
            pass
        self.wm_geometry("%dx%d+%s+%s"%(w, h, x, y))
        self.wm_title("devparrot")

        self.protocol('WM_DELETE_WINDOW', quit)

        if PhotoImage:
            resource = resource_stream(__name__, 'resources/icon48.png')
            img = PhotoImage(Image.open(resource))
            self.tk.call('wm', 'iconphoto', self._w, img)


        self._vbox = ttk.Tkinter.Frame(self)
        self._vbox.pack(expand=True, fill=ttk.Tkinter.BOTH)
        
        self.entry = controlerEntry.ControlerEntry(self._vbox)

        self.hpaned = ttk.PanedWindow(self._vbox, orient=ttk.Tkinter.HORIZONTAL)
        self.hpaned.pack(expand=True, fill=ttk.Tkinter.BOTH)

        self.vpaned = ttk.PanedWindow(self.hpaned, orient=ttk.Tkinter.VERTICAL)
        self.vpaned.pack(expand=True, fill=ttk.Tkinter.BOTH)

        self.globalContainer = ttk.Frame(self.vpaned, borderwidth=1, padding=0, relief="ridge")
        self.vpaned.add(self.globalContainer)

        self.hpaned.add(self.vpaned)

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
        import traceback, tkMessageBox
        err = ''.join(traceback.format_exception(*args))
        session.logger.error(err)
        tkMessageBox.showerror('Exception', "An exception occurs\nPlease report to devparrot team", detail=err)
    
    def get_globalContainer(self):
        return self.globalContainer
        
    def focus_and_break(self, event):
        self.entry.focus()
        return "break"


