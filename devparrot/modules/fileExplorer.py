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
import os, re

from fnmatch import fnmatch
from devparrot.core import session
from devparrot.core.modules import BaseModule

hasImageSupport = True
try:
    from PIL import Image, ImageTk
except ImportError:
    try:
        import Image, ImageTk
    except ImportError:
        hasImageSupport = False
try:
    from xdg import Mime
    from xdg.IconTheme import getIconPath
except ImportError:
    # we cannot get icon for a mime
    hasImageSupport = False


tkImages = {}

def _generate_all_mime_combination(mimeType):
    for i in range(len(mimeType), 0, -1):
        yield tuple(mimeType[:i]), "-".join(mimeType[:i])
        yield tuple(mimeType[:i]), "%s%s"%("gnome-mime-", "-".join(mimeType[:i]))

class FileExplorer(BaseModule):
    @staticmethod
    def update_config(config):
        config.add_option("iconTheme", default=None)
        config.add_option("showIcon", default=False)
        config.add_option("excludes", default=["*.pyc", "*.pyo", "*.o", "__pycache__", ".git*"])

    def activate(self):
        self.fileExplorerView = FileExplorerView(session.window, self)
        session.helperManager.add_helper(self.fileExplorerView, "fileExplorer", 'left')

    def deactivate(self):
        session.helperManager.remove_helper(self.fileExplorerView, 'left')
        self.fileExplorerView = None

    def on_configChanged(self, var, key, old):
        if var.name in ("iconTheme", "showIcon"):
            return _on_iconTheme_changed()

    def _on_iconTheme_changed(self):
        global tkImages
        tkImages = {}
        if self.active:
            session.window.after_idle(self.fileExplorerView.filltree)

    def _load_icon_for_mime(self, mimeType):
        if not hasImageSupport:
            return None
        iconPath = getIconPath(mimeType, size=16, theme=session.config.get('iconTheme'), extensions=["png", "xpm"])
        if iconPath:
            iconImage = Image.open(iconPath)
            return ImageTk.PhotoImage(iconImage)
        return None

    def _get_icon_for_mime(self, mimeType):
        if not session.config.get('showIcon'):
            return None
        passedMime = set()
        for mimekey, mimetext in _generate_all_mime_combination(mimeType):
            if mimekey in tkImages:
                return tkImages[mimekey]
            image = self._load_icon_for_mime(mimetext)
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

    def apply_exclude(self, entry):
        for filter_ in session.config.get('excludes'):
            if fnmatch(entry, filter_):
                return False
        return True

class FileExplorerView(tkinter.ttk.Frame):
    def __init__(self,parent, module):
        tkinter.ttk.Frame.__init__(self, parent)
        self.module = module
        self.vScrollbar = tkinter.ttk.Scrollbar(self, orient=tkinter.VERTICAL)
        self.vScrollbar.grid(column=1, row=0, sticky="nsew")
        self.treeView = tkinter.ttk.Treeview(self)
        self.treeView.grid(column=0, row=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)

        self.treeView.column('#0')
        self.treeView['selectmode'] =(tkinter.BROWSE)
        self.treeView.bind('<Double-Button-1>', self.on_double_click)

        self.vScrollbar['command'] = self.treeView.yview
        self.treeView['yscrollcommand'] = self.vScrollbar.set

        self.treeView.bind('<<TreeviewOpen>>', self.on_open)

        bindtags = list(self.treeView.bindtags())
        bindtags.insert(1,"devparrot")
        bindtags = " ".join(bindtags)
        self.treeView.bindtags(bindtags)
        self.currentPath = os.getcwd()
        self._pending_filltree = None
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

    def insert_child(self, parent, name, image):
        parent = os.path.relpath(parent, self.currentPath)
        if parent == '.':
            parent = ''
        iid = os.path.join(parent, name)
        args = {'iid':iid, 'text':name}
        if image:
            args['image'] = image
        self.treeView.insert(parent, 'end', **args)

    def on_open(self, event):
        selection = self.treeView.selection()
        if not selection:
            return
        fullPath = os.path.join(self.currentPath, selection[0])
        fullPath = os.path.abspath(fullPath)
        parent = os.path.relpath(fullPath, self.currentPath)
        self._filltree(parent)

    def filltree(self):
        if self._pending_filltree:
            return
        self._pending_filltree = self.after_idle(self._filltree)

    def _filltree(self, root=''):
        self._pending_filltree = None
        self.treeView.heading('#0', text=os.path.basename(self.currentPath))
        while len(self.treeView.get_children(root)):
            self.treeView.delete(self.treeView.get_children(root)[0])
        if not root:
            image = self.module._get_icon_for_mime(("folder",))
            self.insert_child(self.currentPath, '..', image)
        for current, dirs, files in os.walk(os.path.join(self.currentPath, root)):
            for dir_ in sorted(dirs):
                if not self.module.apply_exclude(dir_):
                    continue
                image = self.module._get_icon_for_mime(("folder",))
                self.insert_child(current,  dir_, image)
                self.insert_child(os.path.join(current, dir_), '.', image=None)
            dirs[:] = []
            for file_ in sorted(files):
                if not self.module.apply_exclude(file_):
                    continue
                image = None
                if hasImageSupport:
                    fullPath = os.path.join(current, file_)
                    mime = str(Mime.get_type_by_name(fullPath)).split('/')
                    image = self.module._get_icon_for_mime(mime)
                self.insert_child(current, file_, image)

