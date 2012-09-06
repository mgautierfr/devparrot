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


import os
import ttk

from devparrot.core import popupMenu as popupMenuModule
import controlerEntry

class Helper:
    def __init__(self):
        global window
        self.window = window

    def ask_questionYesNo(self, title, message):
        import tkMessageBox
        return tkMessageBox.askyesno(title, message)

    def ask_filenameSave(self, *args, **kwords):
        import tkFileDialog
        response = tkFileDialog.asksaveasfilename(title="Save a file", *args, **kwords)
        return response

    def ask_filenameOpen(self, *args, **kwords):
        import tkFileDialog
        response = tkFileDialog.askopenfilename(title="Open a file", *args, **kwords)
        return response

window = None
entry = None
workspaceContainer = None
hpaned = None
vpaned = None
popupMenu = None

def quit(event):
    from actions.controlerActions import quit
    quit.run()

def init():
    from devparrot.core import config
    global window
    global entry
    global workspaceContainer
    global hpaned
    global vpaned
    global popupMenu
    window = ttk.Tkinter.Tk()
    style = ttk.Style()
    style.configure("notFoundStyle.TEntry", fieldbackground=config.color.notFoundColor)
    style.configure("okStyle.TEntry", fieldbackground=config.color.okColor)
    style.configure("errorStyle.TEntry", fieldbackground=config.color.errorColor)
    geom = window.wm_geometry()
    x = geom.split('+')[1]
    y = geom.split('+')[2]
    window.wm_geometry("%dx%d+%s+%s"%(config.window.width,config.window.height,x,y))
    icon_path = os.path.dirname(os.path.realpath(__file__))
    icon_path = os.path.join(icon_path,"../resources/icon.png")
#	window.wm_iconwindow(icon_path)
    window.wm_title("DevParrot")

    vbox = ttk.Tkinter.Frame(window)
    vbox.pack(expand=True,fill=ttk.Tkinter.BOTH)
    entry = controlerEntry.ControlerEntry(vbox)

    hpaned = ttk.PanedWindow(vbox,orient=ttk.Tkinter.HORIZONTAL)
    hpaned.pack(expand=True,fill=ttk.Tkinter.BOTH)

    vpaned = ttk.PanedWindow(hpaned,orient=ttk.Tkinter.VERTICAL)
    vpaned.pack(expand=True,fill=ttk.Tkinter.BOTH)

    workspaceContainer = ttk.Frame(vpaned, borderwidth=1, padding=0, relief="ridge")
    vpaned.add(workspaceContainer)

    hpaned.add(vpaned)


    popupMenu = popupMenuModule.Menu()

    def focus_and_break(event):
        entry.focus()
        return "break"

    window.bind_class("Command", "<Control-Return>", focus_and_break)
    window.bind('<ButtonRelease>', lambda e: popupMenu.unpost() )
    window.bind('<Configure>', lambda e: popupMenu.unpost() )
    bindtags = list(window.bindtags())
    bindtags.insert(1,"Command")
    bindtags = " ".join(bindtags)
    window.bindtags(bindtags)

    from devparrot.core import command
    command.binder.bind()

def add_helper(widget, pos):
    global hpaned
    global vpaned
    if pos == 'left':
        hpaned.insert(0, widget)
    if pos == 'right':
        hpaned.insert('end', widget)
    if pos == 'top':
        vpaned.insert(0, widget)
    if pos == 'bottom':
        vpaned.insert('end', widget)


