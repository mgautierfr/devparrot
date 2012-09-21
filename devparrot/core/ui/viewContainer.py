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

import Tkinter,ttk,Tkdnd
from devparrot.core import session
from devparrot.core.utils.variable import fcb, proxy, ref

class ContainerChild():
    def __init__(self):
        self.parentContainer = None
    
    def get_parentContainer(self) : return self.parentContainer
    def set_parentContainer(self, parent):
            self.parentContainer = parent

class TopContainer(ContainerChild,Tkinter.Frame):
    def __init__(self):
        ContainerChild.__init__(self)
        Tkinter.Frame.__init__(self,session.get_globalContainer()) 
        self.pack(expand=True, fill=ttk.Tkinter.BOTH)
        session.get_globalContainer().dnd_accept = self.dnd_accept
        self.init_default()
    
    def dnd_accept(self, source, event):
        x, y = event.x_root, event.y_root
        target_widget = None
        for notebook in NotebookContainer.notebookList:
            x1 = notebook.winfo_rootx()
            x2 = x1 + notebook.winfo_width()
            y1 = notebook.winfo_rooty()
            y2 = y1 + notebook.winfo_height()
            if x>x1 and x<x2 and y>y1 and y<y2:
                target_widget = notebook
                break
        if target_widget :
            return target_widget.dnd_accept(source, event)
        return None
        
    
    def init_default(self):
        container = NotebookContainer()
        self.attach_child(container)
        container.set_as_current()
    
    def attach_child(self, container):
        self.container = container
        self.container.set_parentContainer(self)
        self.container.pack(in_=self, expand=True, fill=ttk.Tkinter.BOTH)
        try : container.register()
        except : pass
    
    def detach_child(self, childToDetach): 
        childToDetach.pack_forget()
        childToDetach.set_parentContainer(None)
        self.childContainer = None
        try : childToDetach.unregister()
        except : pass
    
    def set_as_current(self):
        self.container.set_as_current()


class SplittedContainer(ContainerChild,Tkinter.PanedWindow):
    def __init__(self, isVertical):
        ContainerChild.__init__(self)
        Tkinter.PanedWindow.__init__(self, session.get_globalContainer(),
                                     orient=Tkinter.VERTICAL if isVertical else Tkinter.HORIZONTAL,
                                     sashrelief="raised",
                                     borderwidth=0,
                                     sashwidth=3,
                                     opaqueresize=False)
        self.uiSubContainer1 = ttk.Frame(self, borderwidth=0, padding=0)
        self.add(self.uiSubContainer1)
        self.uiSubContainer2 = ttk.Frame(self, borderwidth=0, padding=0)
        self.add(self.uiSubContainer2)
        self.container1 = None
        self.container2 = None
        self.isVertical = isVertical
        if isVertical:
            self.set_panedPos = self.set_vPanedPos
        else:
            self.set_panedPos = self.set_hPanedPos
    
    def set_vPanedPos(self, pos):
        height = self.winfo_height()
        self.sash_place(0, 0, int(height*pos))
    def set_hPanedPos(self, pos):
            width = self.winfo_width()
            self.sash_place(0, int(width*pos),0)
        
    def init(self, container1, container2):
        self.attach_child(container1)
        self.attach_child(container2)
    
    def attach_child(self, child):
        try : child.register()
        except : pass
        if self.container1 == None:
            self.container1 = child
            child.pack(in_=self.uiSubContainer1, expand=True, fill=ttk.Tkinter.BOTH)
            child.set_parentContainer(self)
        elif self.container2 == None:
            self.container2 = child
            child.pack(in_=self.uiSubContainer2, expand=True, fill=ttk.Tkinter.BOTH)
            child.set_parentContainer(self)
    
    def detach_child(self, childToDetach):
        childToDetach.set_parentContainer(None)
        childToDetach.pack_forget()
        try : childToDetach.unregister()
        except : pass
        if self.container1 == childToDetach:
            self.container1 = None
        elif self.container2 == childToDetach:
            self.container2 = None
    
    def lift(self):
        self.container1.lift()
        self.container2.lift()
        
    def destroy_tree(self):
        if self.container1:
            container = self.container1
            self.detach_child(container)
            container.destroy_tree()
        if self.container2:
            container = self.container2
            self.detach_child(container)
            container.destroy_tree()

        self.remove(self.uiSubContainer1)
        self.remove(self.uiSubContainer2)
        self.uiSubContainer1 = None
        self.uiSubContainer2 = None	
    
    def set_as_current(self):
        if self.container1:
            self.container1.set_as_current()
        elif self.container2:
            self.container2.set_as_current()

    def find_notebook_different_of(self, badNotebook=False):
        testContainer = self.container1
        if testContainer == badNotebook:
            testContainer = self.container2
        if isinstance(testContainer, NotebookContainer):
            return testContainer
        else:
            return testContainer.find_notebook_different_of()	

def on_drag_begin_notebook(event):
    event.num = 1
    notebook = event.widget
    documentViewIndex = notebook.index("@%d,%d"%(event.x,event.y))
    if documentViewIndex != "":
        documentView = notebook._children[documentViewIndex]
        Tkdnd.dnd_start(documentView, event)		

def on_button_pressed(event):
    return "break"

def on_button_released(event):
    try:
        event.widget.select("@%d,%d"%(event.x,event.y))
    except Tkinter.TclError:
        pass

class NotebookContainer(ContainerChild, ttk.Notebook):
    notebookList = set()
    current = None
    initialized = False
    
    def __init__(self):
        ContainerChild.__init__(self)
        ttk.Notebook.__init__(self, session.get_globalContainer(), padding=0)
        self._children = []
        self.drag_handler = None
        if not NotebookContainer.initialized:
            self.bind_class("Drag", "<Button-1><Button1-Motion>", on_drag_begin_notebook)
            self.bind_class("Drag", "<Button-1>", on_button_pressed)
            self.bind_class("Drag", "<ButtonRelease-1>", on_button_released)
            NotebookContainer.initialized=True
        self.bindtags(" ".join(["Drag"]+[t for t in self.bindtags()]))
        self.bind("<<NotebookTabChanged>>",self.on_tabChanged)
    
    def register(self):
        NotebookContainer.notebookList.add(self)
    
    def unregister(self):
        NotebookContainer.notebookList.remove(self)
    
    def dnd_accept(self, source, event):
        if str(source) == str(self.select()) and len(self._children)==1:
            return None
        if not self.drag_handler:
            self.drag_handler = DragHandler(self)
        return self.drag_handler
    
    def destroy_dnd(self):
        if self.drag_handler:
            self.drag_handler.destroy()
            self.drag_handler = None
    
    def attach_child(self, child):
        child.set_parentContainer(self)
        self._children.append(child)
        self.add(child, text=child.document.title)
        child.document.title_register(fcb(lambda v,o, s=proxy(self), child=proxy(child): s.change_title(child), ref(self)))
    
    def change_title(self, child):
        self.tab(child, text=child.document.title)
    
    def detach_child(self, child):
        child.set_parentContainer(None)
        self.forget(child)
        self._children.remove(child)
    
    def set_documentView(self, documentView):
        if documentView:
            self.attach_child(documentView)
            self.select(documentView)

    def get_documentView(self):
        selected = self.select()
        if selected :
            return self.nametowidget(selected)
        return None

    def get_nbChildren(self):
        return len(self._children)
    
    def destroy_tree(self):
        for win in self._children:
            self.detach_child(win)

    def lift(self):
        ttk.Notebook.lift(self, self.parentContainer)
        for win in self._children:
            win.lift()
    
    def set_as_current(self):
        NotebookContainer.current = self

    def on_tabChanged(self, arg):
        selected = self.select()
        if selected:
            self.nametowidget(selected).focus()

def split(documentView, direction, first=True):
    notebook = documentView.get_parentContainer()
    if len(notebook._children) == 1:
        # can't split if only one child
        return False

    notebook.detach_child(documentView)
    parent = notebook.get_parentContainer()
    parent.detach_child(notebook)
    
    splitted = SplittedContainer(direction!=0)
    parent.attach_child(splitted)
    
    newNotebook = NotebookContainer()
    newNotebook.set_documentView(documentView)
    
    if first:
        splitted.init(newNotebook, notebook)
    else:
        splitted.init(notebook, newNotebook)
    
    splitted.lift()
    
    splitted.update()
    splitted.after_idle(splitted.set_panedPos,0.5)
    
    newNotebook.set_as_current()
    return True
    
def unsplit(documentView):
    if isinstance(documentView, NotebookContainer):
        unsplit_notebook(documentView)
    else:
        otherNotebook = unsplit_notebook(documentView.get_parentContainer())
        if otherNotebook:
            otherNotebook.select(documentView)
    return True

def unsplit_notebook(notebook):
    parent = notebook.get_parentContainer()
    if not isinstance(parent, SplittedContainer):
        return
    
    grandParent = parent.get_parentContainer()
    
    leftnotebook = parent.find_notebook_different_of(notebook)
    
    if notebook == parent.container1:
        goodChild = parent.container2
    else:
        goodChild = parent.container1

    for view in list(notebook._children):
        notebook.detach_child(view)
        leftnotebook.attach_child(view)
    
    parent.detach_child(notebook)
    parent.detach_child(goodChild)
    grandParent.detach_child(parent)
    parent.destroy_tree()
    parent.destroy()
    
    grandParent.attach_child(goodChild)
    
    goodChild.lift()
    leftnotebook.set_as_current()
    return leftnotebook

class DragHandler(ttk.Tkinter.Toplevel):
    def __init__(self, container):
        from devparrot.core import ui
        ttk.Tkinter.Toplevel.__init__(self, ui.window)
        self.container = container
        self.init()
        
    def init(self):
        self.wm_overrideredirect(True)
        self.pos = 'center'
        r = "%(width)dx%(height)d+%(X)d+%(Y)d"%{
            "width"  : self.container.winfo_width(),
            "height" : self.container.winfo_height(),
            "X"      : self.container.winfo_rootx(),
            "Y"      : self.container.winfo_rooty()
            }
        self.wm_geometry(r)
        
    def calculate_pos(self,x,y):
        geom = {
         'width' : self.container.winfo_width(),
         'height': self.container.winfo_height(),
         'x'     : self.container.winfo_rootx(),
         'y'     : self.container.winfo_rooty(),
        }
        geom['x2'] = geom['x']+geom['width']
        geom['y2'] = geom['y']+geom['height']
        geom['cx'] = geom['x']+geom['width']/2
        geom['cy'] = geom['y']+geom['height']/2
        
        pos = 'center'
        
        if (abs(x-geom['cx']) > geom['width']/4) or (abs(y-geom['cy']) > geom['height']/4):
            l = []
            l.append(( abs(x-geom['x'])  , 'left'   ))
            l.append(( abs(x-geom['x2']) , 'right'  ))
            l.append(( abs(y-geom['y'])  , 'top'    ))
            l.append(( abs(y-geom['y2']) , 'bottom' ))
            pos = min(l)[1]
        return pos
        
    def dnd_accept(self, source, event):
        return self
    
    def dnd_enter(self, source, event):
        pass
    
    def dnd_leave(self, source, event):
        self.container.destroy_dnd()
        pass
    
    def dnd_motion(self, source, event):
        x, y = event.x_root, event.y_root
        new = {
            "width"  : self.container.winfo_width(),
            "height" : self.container.winfo_height(),
            "X"      : self.container.winfo_rootx(),
            "Y"      : self.container.winfo_rooty()
        }		
        self.pos = self.calculate_pos(x,y)
        if self.pos == 'left':
            new['width'] /= 2
        if self.pos == 'right':
            new['width'] /= 2
            new['X'] += new['width']
        if self.pos == 'top':
            new['height'] /= 2
        if self.pos == 'bottom':
            new['height'] /= 2
            new['Y'] += new['height']

        self.wm_geometry("%(width)dx%(height)d+%(X)d+%(Y)d"%new)
        return True
    
    def dnd_commit(self, source, event):
        x, y = event.x_root, event.y_root
        pos = self.calculate_pos(x,y)
        self.container.destroy_dnd()
        
        document = source.document
        documentView = document.documentView
        notebook = documentView.get_parentContainer()
        parent = notebook.get_parentContainer()

        if len(notebook._children) == 1:
            grandParent = parent.get_parentContainer()
            if notebook == parent.container1:
                goodChild = parent.container2
            else:
                goodChild = parent.container1
    
            parent.detach_child(notebook)
            parent.detach_child(goodChild)
            grandParent.detach_child(parent)
            parent.destroy_tree()
            parent.destroy()
        
            grandParent.attach_child(goodChild)				
        
        notebook.detach_child(documentView)
        
        if pos == 'center':
            self.container.set_documentView(documentView)
            self.container.lift()
            self.container.set_as_current()
        else:
            parent = self.container.get_parentContainer()
            parent.detach_child(self.container)
    
            splitted = SplittedContainer(pos in ['top','bottom'])
            parent.attach_child(splitted)
    
            newNotebook = NotebookContainer()
            newNotebook.set_documentView(documentView)
    
            if pos in ['left', 'top']:
                splitted.init(newNotebook, self.container)
            else:
                splitted.init(self.container, newNotebook)
    
            splitted.lift()
    
            splitted.update()
            splitted.after_idle(splitted.set_panedPos,0.5)
    
            newNotebook.set_as_current()
