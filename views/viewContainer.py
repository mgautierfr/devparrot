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

class ContainerSpecialization(object):
	def __init__(self, specialized):
		# remove the connection from the old specialization to the specialized
		if specialized.__specialization__:
			specialized.__specialization__.specialized = None
		# set the new specialization
		self.specialized = specialized
		self.specialized.__specialization__ = self
		
class AbstractContainerChild(object):
	def __init__(self):
		self.parentContainer = None
	
	def get_parentContainer(self) : return self.parentContainer
	def set_parentContainer(self, parent):
			self.parentContainer = parent
			
class Specializable(object):
	def __init__(self):
		self.__specialization__ = None
	
	def __getattr__(self, name):
		if self.__dict__['__specialization__'] != None :
			att = getattr(self.__dict__['__specialization__'],name)
			import types
			if isinstance(att, types.MethodType):
				#take the correspondinf function
				att = att.im_func
				#return the new bounded method
				return att.__get__(self, self.__class__)
			else:
				return att
		raise AttributeError
	
	def __setattr__(self, name, value):
		if '__specialization__' not in self.__dict__ or self.__dict__['__specialization__'] == None or name =='__specialization__' :
			object.__setattr__(self, name, value)
			return

		if name in self.__dict__['__specialization__'].__dict__:
			object.__setattr__(self.__dict__['__specialization__'], name, value)
		else:
			object.__setattr__(self, name, value)

class BasicContainer(AbstractContainerChild,Specializable):
	def __init__(self):
		AbstractContainerChild.__init__(self)
		Specializable.__init__(self)
	
	def get_parentContainer(self) : return self.parentContainer
	def set_parentContainer(self, parent) :
		if isinstance(self.__specialization__, LeafSpecialization):
			if parent:
				LeafSpecialization.leafList.append(self.__specialization__)
			else:
				LeafSpecialization.leafList.remove(self.__specialization__)
		self.parentContainer = parent

class TopContainer(BasicContainer):
	def __init__(self):
		BasicContainer.__init__(self)
		TopSpecialization(self)
	
def CleanSpecialization(specialized):
	if specialized.__specialization__:
		specialized.__specialization__.specialized = None
	specialized.__specialization__ = None

class SplittedSpecialization(ContainerSpecialization):
	def __init__(self, specialized):
		ContainerSpecialization.__init__(self, specialized)
		self.container1 = None
		self.container2 = None
		
	def init(self, container1, container2):
		self.container1 = container1
		self.container2 = container2
		container1.uiContainer.pack(in_=self.uiSubContainer1, expand=True, fill=ttk.Tkinter.BOTH)
		container2.uiContainer.pack(in_=self.uiSubContainer2, expand=True, fill=ttk.Tkinter.BOTH)
		container1.set_parentContainer(self)
		container2.set_parentContainer(self)
	
	def lift(self):
		#self.uiContainer.lift(self.parentContainer.uiContainer)
		self.container1.lift()
		self.container2.lift()
			
	def __unlink_child__(self):
		if self.container1:
			self.container1.set_parentContainer(None)
			self.container1.uiContainer.forget()
		if self.container2:
			self.container2.set_parentContainer(None)
			self.container2.uiContainer.forget()
		
	def prepare_to_dnd(self, active, toExclude = None):
		if self.container1:
			self.container1.prepare_to_dnd(active, toExclude)
		if self.container2:
			self.container2.prepare_to_dnd(active, toExclude)
		
	def destroy_tree(self):
		if self.container1:
			self.container1.set_parentContainer(None)
			self.container1.uiContainer.forget()
			self.container1.destroy_tree()
			self.container1 = None
		if self.container2:
			self.container2.set_parentContainer(None)
			self.container2.uiContainer.forget()
			self.container2.destroy_tree()
			self.container2 = None

		self.uiContainer.remove(self.uiSubContainer1)
		self.uiContainer.remove(self.uiSubContainer2)
		self.uiSubContainer1 = None
		self.uiSubContainer2 = None
		self.uiContainer = None
		CleanSpecialization(self)
			
	def detach_child(self, childToDetach):
		childToDetach.set_parentContainer(None)
		childToDetach.uiContainer.pack_forget()
		if self.container1 == childToDetach:
			self.container1 = None
		elif self.container2 == childToDetach:
			self.container2 = None
		

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
		print "toKeep :",toKeep
		print "toRemove :",toRemove
				
		fatherContainer = self.get_parentContainer()
		fatherContainer.detach_child(self)
		self.detach_child(toKeep)
		fatherContainer.attach_child(toKeep)
		toKeep.set_as_current()
		self.destroy_tree()
		
	def undisplay(self, toRemove):
		return self.unsplit(toRemove = toRemove)
	
	def ui_attach(self, uiContainer):
		if not self.uiSubContainer1.slaves():
			uiContainer.pack(in_=self.uiSubContainer1, expand=True, fill=ttk.Tkinter.BOTH)
		elif not self.uiSubContainer2.slaves():
			uiContainer.pack(in_=self.uiSubContainer2, expand=True, fill=ttk.Tkinter.BOTH)

	def attach_child(self, child):
		if self.container1 == None:
			self.container1 = child
			child.uiContainer.pack(in_=self.uiSubContainer1, expand=True, fill=ttk.Tkinter.BOTH)
			child.set_parentContainer(self)
		if self.container2 == None:
			self.container2 = child
			child.uiContainer.pack(in_=self.uiSubContainer2, expand=True, fill=ttk.Tkinter.BOTH)
			child.set_parentContainer(self)
	
	def set_as_current(self):
		if self.container1:
			self.container1.set_as_current()
		elif self.container2:
			self.container2.set_as_current()	
		
class HSplittedSpecialization(SplittedSpecialization):
	def __init__(self, specialized): 
		SplittedSpecialization.__init__(self, specialized)
		self.uiContainer = Tkinter.PanedWindow(mainWindow.workspaceContainer,orient=Tkinter.HORIZONTAL, sashrelief="raised",borderwidth=0, sashwidth=3)
		self.uiSubContainer1 = ttk.Frame(self.uiContainer, borderwidth=0, padding=0)
		self.uiContainer.add(self.uiSubContainer1)
		self.uiSubContainer2 = ttk.Frame(self.uiContainer, borderwidth=0, padding=0)
		self.uiContainer.add(self.uiSubContainer2)
	
	def set_panedPos(self, pos):
		width = self.uiContainer.winfo_width()
		self.uiContainer.sash_place(0, int(width*pos),0)

class VSplittedSpecialization(SplittedSpecialization):
	def __init__(self, specialized):
		SplittedSpecialization.__init__(self, specialized)
		self.uiContainer = Tkinter.PanedWindow(mainWindow.workspaceContainer,orient=Tkinter.VERTICAL, sashrelief="raised",borderwidth=0, sashwidth=3)
		self.uiSubContainer1 = ttk.Frame(self.uiContainer, borderwidth=0, padding=0)
		self.uiContainer.add(self.uiSubContainer1)
		self.uiSubContainer2 = ttk.Frame(self.uiContainer, borderwidth=0, padding=0)
		self.uiContainer.add(self.uiSubContainer2)
	
	def set_panedPos(self, pos):
		height = self.uiContainer.winfo_height()
		self.uiContainer.sash_place(0, 0, int(height*pos))
		
class TopSpecialization(ContainerSpecialization):
	def __init__(self, specialized):
		ContainerSpecialization.__init__(self, specialized)
		#self.uiContainer = Tkinter.Frame()
		self.uiContainer = mainWindow.workspaceContainer
		self.uiContainer.dnd_accept = self.dnd_accept 
		self.init_default()
	
	def dnd_accept(self, source, event):
		print "dnd_accept1"
		x, y = event.x_root, event.y_root
		target_widget = None
		for leaf in LeafSpecialization.leafList:
			x1 = leaf.uiContainer.winfo_rootx()
			x2 = x1 + leaf.uiContainer.winfo_width()
			y1 = leaf.uiContainer.winfo_rooty()
			y2 = y1 + leaf.uiContainer.winfo_height()
			if x>x1 and x<x2 and y>y1 and y<y2:
				target_widget = leaf
				break
		if target_widget :
			return target_widget.dnd_accept(source, event)
		return None
		
	
	def init_default(self):
		self.childContainer = BasicContainer()
		LeafSpecialization(self.childContainer)
		self.childContainer.set_parentContainer(self)
		self.ui_attach(self.childContainer.uiContainer)
		self.childContainer.set_as_current()
		#self.gtkContainer.show_all()
	
	def ui_attach(self, uiContainer):
		uiContainer.pack(in_=self.uiContainer, expand=True, fill=ttk.Tkinter.BOTH)
	
	def detach_child(self, childToDetach):
		#import pdb; pdb.set_trace() 
		childToDetach.uiContainer.pack_forget()
		childToDetach.set_parentContainer(None)
		self.childContainer = None
	
	def undisplay(self, toRemove):
		self.detach_child(toRemove)
		toRemove.destroy_tree()
		self.init_default()
	
	def prepare_to_dnd(self, active, toExclude = None):
		self.childContainer.prepare_to_dnd(active, toExclude)
	
	def attach_child(self, child):
		self.childContainer = child
		child.uiContainer.pack(in_=self.uiContainer, expand=True, fill=ttk.Tkinter.BOTH)
		child.set_parentContainer(self)
		#self.gtkContainer.show_all()
	
	def set_as_current(self):
		self.childContainer.set_as_current()

class LeafSpecialization(ContainerSpecialization):
	current = None
	leafList = []
	
	def __init__(self, specialized, uiContainer=None):
		ContainerSpecialization.__init__(self, specialized)
		if uiContainer == None:
			self.uiContainer = ttk.Frame(mainWindow.workspaceContainer, borderwidth=0, padding=0)
		else:
			self.uiContainer = uiContainer
		self.drag_handler = None
		self.documentView = None
	
	def dnd_accept(self, source, event):
		if source == self.documentView:
			return None
		if not self.drag_handler:
			self.drag_handler = DragHandler(self)
		return self.drag_handler

	def init(self, documentView):
		self.set_as_child(documentView)
		self.show_all()

	def destroy_dnd(self):
		if self.drag_handler:
			self.drag_handler.destroy()
			self.drag_handler = None

	def set_documentView(self, documentView):
		if self.documentView:
			self.documentView.forget()
			self.documentView.set_parentContainer(None)
			self.documentView = None
			
		if documentView:
			documentView.set_parentContainer(self)
			self.documentView = documentView
			documentView.pack(in_=self.uiContainer, expand=True, fill=ttk.Tkinter.BOTH)

	def get_documentView(self):
		return self.documentView
		
	def destroy_tree(self):
		if self.documentView:
			self.documentView.set_parentContainer(None)
			self.documentView.forget()
			self.documentView = None

		self.uiContainer = None
		CleanSpecialization(self)
	
	def undisplay(self, toRemove):
		return self.get_parentContainer().undisplay(self)
		
	def split(self, direction, newView, first = False):
		#switch basecontainer to a SplittedContainer
		currentUiContainer = self.uiContainer
		currentDocumentView = self.documentView
		fatherContainer = self.get_parentContainer()
		self.uiContainer.forget()
		
		if direction == 0:
			HSplittedSpecialization(self)
		else:
			VSplittedSpecialization(self)
		fatherContainer.ui_attach(self.uiContainer)

		# create the two leaf containers
		container1 = BasicContainer()
		LeafSpecialization(container1, currentUiContainer)
		currentDocumentView.set_parentContainer(container1)
		container1.documentView = currentDocumentView
		
		 
		container2 = BasicContainer()
		LeafSpecialization(container2)
		container2.set_documentView(newView)

		#add the two leaf containers to the base container
		if first:
			self.init(container2, container1)	
		else:
			self.init(container1, container2)
		
		self.lift()
		#import pdb; pdb.set_trace()
		
		self.uiContainer.update()
		self.uiContainer.after_idle(self.set_panedPos,0.5)
		
		container1.set_as_current()
	
	def lift(self):
		self.uiContainer.lift(self.parentContainer.uiContainer)
		self.documentView.lift()
	
	def set_as_current(self):
		LeafSpecialization.current = self

class DragHandler(ttk.Tkinter.Toplevel):
	def __init__(self, container):
		ttk.Tkinter.Toplevel.__init__(self, mainWindow.window)
		self.container = container
		self.init()
		
	def init(self):
		self.wm_overrideredirect(True)
		self.pos = 'center'
		r = "%(width)dx%(height)d+%(X)d+%(Y)d"%{
		    "width"  : self.container.uiContainer.winfo_width(),
		    "height" : self.container.uiContainer.winfo_height(),
		    "X"      : self.container.uiContainer.winfo_rootx(),
		    "Y"      : self.container.uiContainer.winfo_rooty()
		    }
		self.wm_geometry(r)
		print r
		
	def calculate_pos(self,x,y):
		geom = {
		 'width' : self.container.uiContainer.winfo_width(),
		 'height': self.container.uiContainer.winfo_height(),
		 'x'     : self.container.uiContainer.winfo_rootx(),
		 'y'     : self.container.uiContainer.winfo_rooty(),
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
		print "drag_enter"
		pass
	
	def dnd_leave(self, source, event):
		print "drag_leave"
		self.container.destroy_dnd()
		pass
	
	def dnd_motion(self, source, event):
		x, y = event.x_root, event.y_root
		print "drag_motion",x,y
		new = {
		    "width"  : self.container.uiContainer.winfo_width(),
		    "height" : self.container.uiContainer.winfo_height(),
		    "X"      : self.container.uiContainer.winfo_rootx(),
		    "Y"      : self.container.uiContainer.winfo_rooty()
		}		
		self.pos = self.calculate_pos(x,y)
		print self.pos
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
		print new
		return True
	
	def dnd_commit(self, source, event):
		print "dnd_commit"
		import core.controler
		x, y = event.x_root, event.y_root
		pos = self.calculate_pos(x,y)
		document = source.document
		self.container.destroy_dnd()
		# unprepare dnd before changing everything
		#core.controler.currentSession.get_workspace().prepare_to_dnd(False)
		if document.documentView.is_displayed():
			parentContainer = document.documentView.get_parentContainer()
			print "parentContainer :",parentContainer
			parentContainer.get_parentContainer().unsplit(toRemove=parentContainer)
		if pos == 'center':
			self.container.set_documentView(document.documentView)
		if pos in ['right','left']:
			self.container.specialized.split(0, document.documentView, first=(pos=='left'))
		if pos in ['top','bottom']:
			self.container.specialized.split(1, document.documentView, first=(pos=='top'))