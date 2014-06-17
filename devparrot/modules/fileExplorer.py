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


import Tkinter,ttk
import os, re

from xdg.IconTheme import getIconPath
from xdg import Mime

from devparrot.core import ui, session

fileExplorerView = None
tkImages = {}
configSection = None
pending_filltree = None
handlers = []

def init(_configSection, name):
    global configSection
    configSection = _configSection
    configSection.add_variable("iconTheme", None)
    configSection.add_variable("showIcon", False)
    configSection.add_variable("excludes", ["*.pyc", "*.pyo", "*.o"])
    configSection.active.register(activate)

def activate(var, old):
    global fileExplorerView
    if var.get():
        fileExplorerView = FileExplorerView(ui.window)
        ui.helperManager.add_helper(fileExplorerView, "fileExplorer", 'left')
        handlers.append(configSection.iconTheme.register(on_iconTheme_changed))
        handlers.append(configSection.showIcon.register(on_iconTheme_changed))
    else:
        [h.unregister() for h in handlers]
        handlers[:] = []
        ui.helperManager.remove_helper(fileExplorerView, 'left')
        fileExplorerView = None
        pass

def on_iconTheme_changed(var, old):
    global tkImages
    tkImages = {}
    if configSection.active.get():
        ui.window.after_idle(fileExplorerView.filltree)

def _load_icon_for_mime(mimeType):
    try:
        from PIL import Image, ImageTk
    except ImportError:
        try:
            import Image, ImageTk
        except ImportError:
            return None
    iconPath = getIconPath(mimeType, size=16, theme=configSection.get("iconTheme"), extensions=["png", "xpm"])
    if iconPath:
        iconImage = Image.open(iconPath)
        return ImageTk.PhotoImage(iconImage)
    return None

def _generate_all_mime_combination(mimeType):
    for i in xrange(len(mimeType), 0, -1):
        yield tuple(mimeType[:i]), "-".join(mimeType[:i])
        yield tuple(mimeType[:i]), "%s%s"%("gnome-mime-", "-".join(mimeType[:i]))

def _get_icon_for_mime(mimeType):
    global tkImages
    if not configSection.get("showIcon"):
        return None
    passedMime = set()
    for mimekey, mimetext in _generate_all_mime_combination(mimeType):
        if mimekey in tkImages:
            return tkImages[mimekey]
        image = _load_icon_for_mime(mimetext)
        if not image:
            passedMime.add(mimekey)
        else:
            for passed in passedMime:
                tkImages[passed] = image
            tkImages[mimekey] = image
            return image
    for passed in passedMime:
        tkImages[passed] = None
    return None

def FileComparator(rootpath):
    class PseudoKey(object):
        def __init__(self, entry, *args):
            self.entry = entry
            self.isdir = os.path.isdir(os.path.join(rootpath, entry))
        def __lt__(self, other):
            if self.isdir and not other.isdir:
                return True
            if not self.isdir and other.isdir:
                return False
            return self.entry < other.entry
        def __gt__(self, other):
            return not self<other
        def __eq__(self, other):
            return self.entry == other.entry
        def __le__(self, other):
            if self.entry == other.entry:
                return True
            return self<other
        def __ge__(self, other):
            if self.entry == other.entry:
                return True
            return not self<other
        def __ne__(self, other):
            return self.entry != other.entry
    return PseudoKey

def apply_exclude(entry):
    from fnmatch import fnmatch
    for filter_ in configSection.excludes.get():
        if fnmatch(entry, filter_):
            return False
    return True

class FileExplorerView(ttk.Frame):
    def __init__(self,parent):
        ttk.Frame.__init__(self, parent)
        self.vScrollbar = ttk.Scrollbar(self, orient=ttk.Tkinter.VERTICAL)
        self.vScrollbar.grid(column=1, row=0, sticky="nsew")
        self.treeView = ttk.Treeview(self)
        self.treeView.grid(column=0, row=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)

        self.treeView.column('#0')
        self.treeView['selectmode'] =(Tkinter.BROWSE)
        self.treeView.bind('<Double-Button-1>', self.on_double_click)

        self.vScrollbar['command'] = self.treeView.yview
        self.treeView['yscrollcommand'] = self.vScrollbar.set

        bindtags = list(self.treeView.bindtags())
        bindtags.insert(1,"devparrot")
        bindtags = " ".join(bindtags)
        self.treeView.bindtags(bindtags)
        self.currentPath = os.getcwd()
        self.filltree()

    def on_double_click(self, event):
        from devparrot.core import session
        selection = self.treeView.selection()
        if selection:
            fullPath = os.path.join(self.currentPath, selection[0])
            fullPath = os.path.abspath(fullPath)
            if os.path.isdir(fullPath):
                self.currentPath = fullPath
                self.filltree()
            else:
                session.commandLauncher.run_command_nofail('open "{}"'.format(fullPath))

    def insert_child(self, iid, text, image):
        args = {'iid':iid, 'text':text}
        if image:
            args['image'] = image
        self.treeView.insert('', 'end', **args)

    def filltree(self):
        global pending_filltree
        if pending_filltree:
            return
        pending_filltree = self.after_idle(self._filltree)

    def _filltree(self):
        global pending_filltree
        pending_filltree = None
        self.treeView.heading('#0', text=os.path.basename(self.currentPath))
        while len(self.treeView.get_children('')):
            self.treeView.delete(self.treeView.get_children('')[0])
        children = os.listdir(self.currentPath)
        children = [ c for c in children if apply_exclude(c) ]
        children = sorted(children, key=FileComparator(self.currentPath))
        image = _get_icon_for_mime(("folder",))
        self.insert_child(os.path.join(self.currentPath, ".."), "..", image)
        for child in children:
            fullPath = os.path.join(self.currentPath, child)
            if os.path.isdir(fullPath):
                image = _get_icon_for_mime(("folder",))
            else:
                mime = str(Mime.get_type_by_name(fullPath)).split('/')
                image = _get_icon_for_mime(mime)
            self.insert_child(fullPath, child, image)

