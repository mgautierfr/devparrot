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

import gtk
from textView import TextView

class AbstractContainer(object):
	def __init__(self, baseContainer):
		self.baseContainer = baseContainer

class BaseContainer(object):
	current = None
	TOP = -1
	LEAF = 0
	VSPLITTED = 1
	HSPLITTED = 2
	def __init__(self):
		self.parentContainer = None
		self.gtkContainer = None
		self.implementation = None
		
	def get_parentContainer(self) : return self.parentContainer
	def set_parentContainer(self, parent) : self.parentContainer = parent
	
	def get_innerContainer(self) : return self.innerContainer
	def set_innerContainer(self, inner) : self.innerContainer = inner
	
	def split(self, direction, newView, first = False): self.implementation.split(direction, newView, first)
	def gtk_attach(self, gtkContainer): self.implementation.gtk_attach(gtkContainer)
	def unsplit(self, toKeep=None, toRemove=None): self.implementation.unsplit(toKeep,toRemove)
	def destroy_tree(self) : self.implementation.destroy_tree()
	def detach_child(self, childToDetach) : self.implementation.detach_child(childToDetach)
	def attach_child(self, child) : self.implementation.attach_child(child)
	def prepare_to_dnd(self, active, toExclude = None) : self.implementation.prepare_to_dnd(active, toExclude)
	def set_documentView(self, documentView) : self.implementation.set_documentView(documentView)
	def get_documentView(self) : return self.implementation.get_documentView()
	
	@staticmethod
	def init_TOP(container):
		container.implementation = TopContainer(container)
	
	@staticmethod
	def init_LEAF(container):
		container.implementation = LeafContainer(container)

	@staticmethod
	def new_VSPLITTED(child1, child2):
		container = BaseContainer()
		container.set_innerContainer(VSplittedContainer(container))
		container.init(child1,child2)
		return container

	@staticmethod
	def new_HSPLITTED(child1, child2):
		container = BaseContainer()
		container.set_innerContainer(HSplittedContainer(container))
		container.init(child1,child2)
		return container	

class SplittedContainer(AbstractContainer):
	def __init__(self, baseContainer):
		AbstractContainer.__init__(self, baseContainer)
		
	def init(self, container1, container2):
		self.container1 = container1
		self.container2 = container2
		self.baseContainer.gtkContainer.pack1(container1.gtkContainer, resize=True)
		self.baseContainer.gtkContainer.pack2(container2.gtkContainer, resize=True)
		container1.set_parentContainer(self.baseContainer)
		container2.set_parentContainer(self.baseContainer)
		self.baseContainer.gtkContainer.show_all()
			
	def __unlink_child__(self):
		if self.container1:
			self.container1.set_parentContainer(None)
			self.remove(self.container1)
		if self.container2:
			self.container2.set_parentContainer(None)
			self.remove(self.container2)
	
	def prepare_to_dnd(self, active, toExclude = None):
		if self.container1:
			self.container1.prepare_to_dnd(active, toExclude)
		if self.container2:
			self.container2.prepare_to_dnd(active, toExclude)
		
	def destroy_tree(self):
		print "destroy tree SPLIT", self, self.container1, self.container2
		if self.container1:
			self.container1.set_parentContainer(None)
			self.baseContainer.gtkContainer.remove(self.container1.gtkContainer)
			self.container1.destroy_tree()
			self.container1 = None
		if self.container2:
			self.container2.set_parentContainer(None)
			self.baseContainer.gtkContainer.remove(self.container2.gtkContainer)
			self.container2.destroy_tree()
			self.container2 = None

		self.baseContainer.gtkContainer = None
		self.baseContainer.implementation = None
		self.baseContainer = None
			
	def detach_child(self, childToDetach):
		childToDetach.set_parentContainer(None)
		self.baseContainer.gtkContainer.remove(childToDetach.gtkContainer)
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
				
		fatherContainer = self.baseContainer.get_parentContainer()
		fatherContainer.detach_child(self.baseContainer)
		self.detach_child(toKeep)
		fatherContainer.attach_child(toKeep)
		self.destroy_tree()
	
	def gtk_attach(self, gtkContainer):
		if self.baseContainer.gtkContainer.get_child1() == None:
			self.baseContainer.gtkContainer.pack1(gtkContainer, resize=True)
		if self.baseContainer.gtkContainer.get_child2() == None:
			self.baseContainer.gtkContainer.pack2(gtkContainer, resize=True)

	def attach_child(self, child):
		if self.container1 == None:
			self.container1 = child
			self.baseContainer.gtkContainer.pack1(child.gtkContainer, resize=True)
			child.set_parentContainer(self.baseContainer)
		if self.container2 == None:
			self.container2 = child
			self.baseContainer.gtkContainer.pack2(child.gtkContainer, resize=True)
			child.set_parentContainer(self.baseContainer)
		self.baseContainer.gtkContainer.show_all()
		
class HSplittedContainer(SplittedContainer):
	def __init__(self, baseContainer):
		SplittedContainer.__init__(self, baseContainer)
		self.baseContainer.gtkContainer = gtk.HPaned()

class VSplittedContainer(SplittedContainer):
	def __init__(self, baseContainer):
		SplittedContainer.__init__(self, baseContainer)
		self.baseContainer.gtkContainer = gtk.VPaned()
		
class TopContainer(AbstractContainer):
	def __init__(self, baseContainer):
		AbstractContainer.__init__(self, baseContainer)
		self.baseContainer.gtkContainer = gtk.VBox()
		self.childContainer = BaseContainer()
		BaseContainer.init_LEAF(self.childContainer)
		self.childContainer.set_parentContainer(self.baseContainer)
		self.gtk_attach(self.childContainer.gtkContainer)
		self.baseContainer.gtkContainer.show_all()
	
	def gtk_attach(self, gtkContainer):
		self.baseContainer.gtkContainer.add(gtkContainer)
	
	def detach_child(self, childToDetach):
		childToDetach.set_parentContainer(None)
		self.baseContainer.gtkContainer.remove(childToDetach.gtkContainer)
		self.childContainer = None
		
	def prepare_to_dnd(self, active, toExclude = None):
		self.childContainer.prepare_to_dnd(active, toExclude)
	
	def attach_child(self, child):
		self.childContainer = child
		self.baseContainer.gtkContainer.add(child.gtkContainer)
		child.set_parentContainer(self.baseContainer)
		self.baseContainer.gtkContainer.show_all()

class LeafContainer(AbstractContainer):

	def __init__(self, baseContainer, gtkContainer=None):
		AbstractContainer.__init__(self, baseContainer)
		if gtkContainer == None:
			self.baseContainer.gtkContainer = gtk.VBox()
		else:
			self.baseContainer.gtkContainer = gtkContainer
		self.drag_handler = None
		self.documentView = None
	
	def init(self, documentView):
		self.set_as_child(documentView)
		self.show_all()
		
	def prepare_to_dnd(self, active, toExclude = None):
		if active:
			if toExclude and self.get_documentView() != toExclude:
				self.drag_handler = DragHandler(self)
		else:
			# the container can be a new created one. So the drag_handler is None
			if self.drag_handler:
				self.drag_handler.hide()
				self.drag_handler.destroy()
				self.drag_handle = None

	def set_documentView(self, documentView):
		print "set_documentView", self.documentView, documentView
		if self.documentView:
			self.baseContainer.gtkContainer.remove(self.documentView)
			self.documentView.set_parentContainer(None)
			self.documentView = None
			
		if documentView:
			documentView.set_parentContainer(self.baseContainer)
			self.documentView = documentView
			self.baseContainer.gtkContainer.add(documentView)
		print "show all"
		self.baseContainer.gtkContainer.show_all()

	def get_documentView(self):
		return self.documentView
		
	def destroy_tree(self):
		print "destroy tree LEAF", self, self.documentView
		if self.documentView:
			self.documentView.set_parentContainer(None)
			self.baseContainer.gtkContainer.remove(self.documentView)
			self.documentView = None

		self.baseContainer.gtkContainer = None
		self.baseContainer.implementation = None
		self.baseContainer = None
		
	def split(self, direction, newView, first = False):
		#switch basecontainer to a SplittedContainer
		currentGtkContainer = self.baseContainer.gtkContainer
		currentDocumentView = self.documentView
		fatherContainer = self.baseContainer.get_parentContainer()
		fatherContainer.gtkContainer.remove(self.baseContainer.gtkContainer)
		
		if direction == 0:
			self.baseContainer.gtkContainer = gtk.HPaned()
		else:
			self.baseContainer.gtkContainer = gtk.VPaned()
		fatherContainer.gtk_attach(self.baseContainer.gtkContainer)
		self.baseContainer.implementation = SplittedContainer(self.baseContainer)

		# create the two leaf containers
		container1 = BaseContainer()
		container1.implementation = LeafContainer(container1, currentGtkContainer)
		self.documentView.set_parentContainer(container1)
		container1.implementation.documentView = self.documentView
		
		 
		container2 = BaseContainer()
		container2.implementation = LeafContainer(container2)
		container2.set_documentView(newView)

		#add the two leaf containers to the base container
		if first:
			self.baseContainer.implementation.init(container2, container1)	
		else:
			self.baseContainer.implementation.init(container1, container2)
		
		BaseContainer.current = container1

class DragHandler(gtk.Window):
	def __init__(self, container):
		gtk.Window.__init__(self,gtk.WINDOW_POPUP)
		self.container = container.baseContainer
		self.drag_dest_set(gtk.DEST_DEFAULT_MOTION|gtk.DEST_DEFAULT_DROP, [('documentView',gtk.TARGET_SAME_APP,5)], gtk.gdk.ACTION_COPY)
		self.connect('drag-motion', self.on_drag_motion)
		self.connect('drag-leave', self.on_drag_leave)
		self.connect('drag-data-received', self.on_drag_data_received)
		self.show()
		self.init()
		
	def init(self):
		r = self.container.gtkContainer.get_allocation()
		p = self.container.gtkContainer.window.get_origin()
		self.pos = 'center'
		self.window.move_resize(r.x+p[0],r.y+p[1],r.width,r.height)
		self.window.set_opacity(0.4)
		
	def calculate_pos(self,x,y):
		r = self.container.gtkContainer.get_allocation()
		if self.pos == 'right':
			x += r.width/2
		if self.pos == 'bottom':
			y += r.height/2
		pos = 'center'
		if (abs(x-r.width/2) > r.width/4) or (abs(y-r.height/2) > r.height/4):
			l = []
			l.append(( abs(x)            , 'left'   ))
			l.append(( abs(x-r.width)    , 'right'  ))
			l.append(( abs(y)            , 'top'    ))
			l.append(( abs(y-r.height)   , 'bottom' ))
			pos = min(l)[1]
		return pos
		
		
	def on_drag_motion(self, widget, drag_context, x, y, time, data=None):		
		r = self.container.gtkContainer.get_allocation()
		p = self.container.gtkContainer.window.get_origin()
		new =  [r.x+p[0],r.y+p[1],r.width,r.height]
		
		self.pos = self.calculate_pos(x,y)
		if self.pos == 'left':
			new[2] -= r.width/2
		if self.pos == 'right':
			new[0] += r.width/2
			new[2] -= r.width/2
		if self.pos == 'top':
			new[3] -= r.height/2
		if self.pos == 'bottom':
			new[1] += r.height/2
			new[3] -= r.height/2
	
		self.drag_highlight()
		self.window.move_resize(*new)
		self.window.set_opacity(0.8)				
		return True
	
	def on_drag_leave(self, widget,drag_context, time, data=None):
		self.drag_unhighlight()
		self.init()
		
	def on_drag_data_received(self, widget, drag_context,  x, y, selection_data, info, time,data=None):
		import core.controler
		pos = self.calculate_pos(x,y)
		document = core.controler.currentSession.get_documentManager().get_file(selection_data.data)
		# unprepare dnd before changing everything
		core.controler.currentSession.get_workspace().prepare_to_dnd(False)
		if document.documentView.is_displayed():
			parentContainer = document.documentView.get_parentContainer()
			parentContainer.get_parentContainer().unsplit(toRemove=parentContainer)
		if pos == 'center':
			self.container.set_documentView(document.documentView)
		if pos in ['right','left']:
			self.container.split(0, document.documentView, first=(pos=='left'))
		if pos in ['top','bottom']:
			self.container.split(1, document.documentView, first=(pos=='top'))

