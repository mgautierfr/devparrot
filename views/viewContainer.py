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
from core import mainWindow
		
class ContainerChild():
	def __init__(self):
		self.parentContainer = None
	
	def get_parentContainer(self) : return self.parentContainer
	def set_parentContainer(self, parent):
			self.parentContainer = parent

class TopContainer(ContainerChild,Tkinter.Frame):
	def __init__(self):
		ContainerChild.__init__(self)
		Tkinter.Frame.__init__(self,mainWindow.workspaceContainer) 
		self.pack(expand=True, fill=ttk.Tkinter.BOTH)
		mainWindow.workspaceContainer.dnd_accept = self.dnd_accept
		self.init_default()
	
	def dnd_accept(self, source, event):
		x, y = event.x_root, event.y_root
		target_widget = None
		for leaf in LeafContainer.leafList:
			x1 = leaf.winfo_rootx()
			x2 = x1 + leaf.winfo_width()
			y1 = leaf.winfo_rooty()
			y2 = y1 + leaf.winfo_height()
			if x>x1 and x<x2 and y>y1 and y<y2:
				target_widget = leaf
				break
		if target_widget :
			return target_widget.dnd_accept(source, event)
		return None
		
	
	def init_default(self):
		container = LeafContainer()
		self.attach_child(container)
		container.set_as_current()
	
	def attach_child(self, container):
		self.container = container
		self.container.set_parentContainer(self)
		self.container.pack(in_=self, expand=True, fill=ttk.Tkinter.BOTH)
		try : container.unregister()
		except : pass
	
	def detach_child(self, childToDetach): 
		childToDetach.pack_forget()
		childToDetach.set_parentContainer(None)
		self.childContainer = None
		try : childToDetach.unregister()
		except : pass
	
	def undisplay(self, toRemove):
		self.detach_child(toRemove)
		toRemove.destroy_tree()
		self.init_default()
	
	def set_as_current(self):
		self.container.set_as_current()


class SplittedContainer(ContainerChild,Tkinter.PanedWindow):
	def __init__(self, isVertical):
		ContainerChild.__init__(self)
		Tkinter.PanedWindow.__init__(self, mainWindow.workspaceContainer,
		                             orient=Tkinter.VERTICAL if isVertical else Tkinter.HORIZONTAL,
		                             sashrelief="raised",
		                             borderwidth=0,
		                             sashwidth=3)
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
	
	def undisplay(self, toRemove):
		return self.unsplit(toRemove = toRemove)
	
	def unsplit(self, toKeep=None, toRemove=None):
		if toRemove == None and toKeep != None:
			if self.container1 == toKeep:
				toRemove = self.container2
			elif self.container2 == toKeep:
				toRemove = self.container1
		elif toKeep == None and toRemove != None:
			if self.container1 == toRemove:
				toKeep = self.container2
			elif self.container2 == toRemove:
				toKeep = self.container1
		else:
			return
			
		fatherContainer = self.get_parentContainer()
		fatherContainer.detach_child(self)
		self.detach_child(toKeep)
		fatherContainer.attach_child(toKeep)
		toKeep.set_as_current()
		self.destroy_tree()
	
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
		

		
class LeafContainer(ContainerChild,ttk.Frame):
	current = None
	leafList = set()
	
	def __init__(self):
		ContainerChild.__init__(self)
		ttk.Frame.__init__(self,mainWindow.workspaceContainer, borderwidth=0, padding=0)
		self.drag_handler = None
		self.documentView = None
	
	def register(self):
		LeafContainer.leafList.add(self)
	
	def unregister(self):
		LeafContainer.leafList.remove(self)
	
	def dnd_accept(self, source, event):
		if source == self.documentView:
			return None
		if not self.drag_handler:
			self.drag_handler = DragHandler(self)
		return self.drag_handler
	
	def attach_child(self, child):
		self.documentView = child
		self.documentView.set_parentContainer(self)
		self.documentView.pack(in_=self, expand=True, fill=ttk.Tkinter.BOTH)
	
	def detach_child(self, child):
		self.documentView.forget()
		self.documentView.set_parentContainer(None)
		self.documentView = None

	def destroy_dnd(self):
		if self.drag_handler:
			self.drag_handler.destroy()
			self.drag_handler = None

	def set_documentView(self, documentView):
		if self.documentView:
			self.detach_child(self.documentView)

		if documentView:
			self.attach_child(documentView)

	def get_documentView(self):
		return self.documentView
		
	def destroy_tree(self):
		if self.documentView:
			self.documentView.set_parentContainer(None)
			self.documentView.forget()
			self.documentView = None
	
	def undisplay(self, toRemove):
		return self.get_parentContainer().undisplay(self)
		
	def split(self, direction, newView, first = False):
		#switch basecontainer to a SplittedContainer
		fatherContainer = self.get_parentContainer()
		fatherContainer.detach_child(self)
		
		splitted = SplittedContainer(direction!=0)

		fatherContainer.attach_child(splitted)
		 
		container2 = LeafContainer()
		container2.set_documentView(newView)

		#add the two leaf containers to the base container
		if first:
			splitted.init(container2, self)	
		else:
			splitted.init(self, container2)
		
		splitted.lift()
		
		splitted.update()
		splitted.after_idle(splitted.set_panedPos,0.5)
		
		container2.set_as_current()
	
	def lift(self):
		ttk.Frame.lift(self, self.parentContainer)
		self.documentView.lift()
	
	def set_as_current(self):
		LeafContainer.current = self

class DragHandler(ttk.Tkinter.Toplevel):
	def __init__(self, container):
		ttk.Tkinter.Toplevel.__init__(self, mainWindow.window)
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
		import core.controler
		x, y = event.x_root, event.y_root
		pos = self.calculate_pos(x,y)
		document = source.document
		# unprepare dnd before changing everything
		self.container.destroy_dnd()
		if document.documentView.is_displayed():
			parentContainer = document.documentView.get_parentContainer()
			parentContainer.get_parentContainer().undisplay(parentContainer)
		if pos == 'center':
			self.container.set_documentView(document.documentView)
		if pos in ['right','left']:
			self.container.split(0, document.documentView, first=(pos=='left'))
		if pos in ['top','bottom']:
			self.container.split(1, document.documentView, first=(pos=='top'))