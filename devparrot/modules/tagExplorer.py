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
import os
from pkg_resources import resource_stream

from devparrot.core import session
from devparrot.core.modules import BaseModule

tkImages = {}

def get_image(type_):
    try:
        return tkImages[type_]
    except KeyError:
        pass
    try:
        from PIL import Image, ImageTk
    except ImportError:
        try:
            import Image, ImageTk
        except ImportError:
            return None
    try:
        resource = resource_stream('devparrot', 'icons/source-%s.png'%type_)
        image = ImageTk.PhotoImage(Image.open(resource))
    except IOError:
        image = None
    tkImages[type_] = image
    return image

tagMap = {}

class BaseProviderMeta(type):
    def __new__(cls, name, bases, dct):
        if name == "BaseProvider":
            return type.__new__(cls, name, bases, dct)
        else:
            _class = type.__new__(cls, name, bases, dct)
            tagMap[name] = _class
            return _class

class BaseProvider(metaclass=BaseProviderMeta):
    pass

class TagExplorer(BaseModule):
    @staticmethod
    def update_config(config):
        config.add_option("tagProvider", default=None)

    def activate(self):
        self.tagExplorerView = TagExplorerView(session.window)
        session.helperManager.add_helper(self.tagExplorerView, "tagExplorer", 'right')

    def deactivate(self):
        session.helperManager.remove_helper(self.tagExplorerView, 'right')
        self.tagExplorerView = None

    def on_currentChanged(self, current, old):
        self.update_tagView()

    def on_save(self, keys):
        self.update_tagView()

    def update_tagView(self):
        document = session.get_currentDocument()
        tagProviderName = document.get_config('tagProvider')
        tagProviderClass = tagMap.get(tagProviderName, None)
        if tagProviderClass:
            tagProvider = tagProviderClass(document.model)
            self.tagExplorerView.filltree(tagProvider)


class BaseTag:
    def __init__(self, position, name, type):
        self.position = position
        self.name = name
        self.type = type
        self.children = []

def TagComparator(rootpath):
    class PseudoKey:
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

class TagExplorerView(tkinter.ttk.Frame):
    def __init__(self,parent):
        tkinter.ttk.Frame.__init__(self,parent)
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

        bindtags = list(self.treeView.bindtags())
        bindtags.insert(1,"devparrot")
        bindtags = " ".join(bindtags)
        self.treeView.bindtags(bindtags)

    def on_double_click(self, event):
        from devparrot.core import session
        selection = self.treeView.selection()
        if selection:
            pos = selection[0]
            session.commandLauncher.run_command('goto "%s"'%pos)
        return "break"

    def insert_child(self, root, tag):
        args = {'iid':tag.position, 'text':tag.name}
        img = get_image(tag.type)
        if img:
            args['image'] = img
        self.treeView.insert(root, 'end', **args)
        
        if tag.type == 'class':
            for child in tag.children:
                self.insert_child(args['iid'], child)

    def filltree(self, provider):
        while len(self.treeView.get_children('')):
            self.treeView.delete(self.treeView.get_children('')[0])
        for tag in provider.get_tag():
            self.insert_child('', tag)
