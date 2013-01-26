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

import Tkinter,ttk
import os

from xdg.IconTheme import getIconPath
from xdg import Mime

from devparrot.core import ui, session

fileExplorerView = None
tkImages = {}
configSection = None

def init(_configSection, name):
    global configSection
    configSection = _configSection
    configSection.add_variable("iconTheme", None)
    configSection.add_variable("showIcon", False)
    configSection.active.register(activate)

def activate(var, old):
    if var.get():
        global fileExplorerView
        fileExplorerView = FileExplorerView(ui.window)
        ui.helperManager.add_helper(fileExplorerView, "fileExplorer", 'left')
        configSection.iconTheme.register(on_iconTheme_changed)
        configSection.showIcon.register(on_iconTheme_changed)
    else:
        pass

def on_iconTheme_changed(var, old):
    global tkImages
    tkImages = {}
    fileExplorerView.filltree()

def _load_icon_for_mime(mimeType):
    import Image, ImageTk
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

class FileExplorerView(ttk.Treeview):
    def __init__(self,parent):
        ttk.Treeview.__init__(self,parent)
        self.column('#0')
        self['selectmode'] =(Tkinter.BROWSE)
        self.bind('<Double-Button-1>', self.on_double_click)
        bindtags = list(self.bindtags())
        bindtags.insert(1,"Command")
        bindtags = " ".join(bindtags)
        self.bindtags(bindtags)
        self.currentPath = os.getcwd()
        self.filltree()

    def on_double_click(self, event):
        from devparrot.core import session
        selection = self.selection()
        if selection:
            fullPath = os.path.join(self.currentPath, selection[0])
            fullPath = os.path.abspath(fullPath)
            if os.path.isdir(fullPath):
                self.currentPath = fullPath
                self.filltree()
            else:
                session.commandLauncher.run_command('open(["%s"])'%fullPath)

    def insert_child(self, iid, text, image):
        args = {'iid':iid, 'text':text}
        if image:
            args['image'] = image
        ttk.Treeview.insert(self, '', 'end', **args)

    def filltree(self):
        self.heading('#0', text=os.path.basename(self.currentPath))
        while len(self.get_children('')):
            self.delete(self.get_children('')[0])
        children = os.listdir(self.currentPath)
        children = sorted(children, key=FileComparator(self.currentPath))
        image = _get_icon_for_mime(("folder",))
        self.insert_child(os.path.join(self.currentPath, ".."), "..", image)
        for child in children:
            fullPath = os.path.join(self.currentPath, child)
            if os.path.isdir(fullPath):
                image = _get_icon_for_mime(("folder",))
            else:
                mime = str(Mime.get_type(fullPath)).split('/')
                image = _get_icon_for_mime(mime)
            self.insert_child(fullPath, child, image)

