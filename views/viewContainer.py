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
	def set_parentContainer(self, parent) : self.parentContainer = parent

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
		self.gtkContainer.pack1(container1.gtkContainer, resize=True)
		self.gtkContainer.pack2(container2.gtkContainer, resize=True)
		container1.set_parentContainer(self)
		container2.set_parentContainer(self)
		self.gtkContainer.show_all()
			
	def __unlink_child__(self):
		if self.container1:
			self.container1.set_parentContainer(None)
			self.gtkContainer.remove(self.container1.gtkContainer)
		if self.container2:
			self.container2.set_parentContainer(None)
			self.gtkContainer.remove(self.container2.gtkContainer)
	
	def prepare_to_dnd(self, active, toExclude = None):
		if self.container1:
			self.container1.prepare_to_dnd(active, toExclude)
		if self.container2:
			self.container2.prepare_to_dnd(active, toExclude)
		
	def destroy_tree(self):
		if self.container1:
			self.container1.set_parentContainer(None)
			self.gtkContainer.remove(self.container1.gtkContainer)
			self.container1.destroy_tree()
			self.container1 = None
		if self.container2:
			self.container2.set_parentContainer(None)
			self.gtkContainer.remove(self.container2.gtkContainer)
			self.container2.destroy_tree()
			self.container2 = None

		self.gtkContainer = None
		CleanSpecialization(self)
			
	def detach_child(self, childToDetach):
		childToDetach.set_parentContainer(None)
		self.gtkContainer.remove(childToDetach.gtkContainer)
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
				
		fatherContainer = self.get_parentContainer()
		fatherContainer.detach_child(self)
		self.detach_child(toKeep)
		fatherContainer.attach_child(toKeep)
		toKeep.set_as_current()
		self.destroy_tree()
		
	def undisplay(self, toRemove):
		return self.unsplit(toRemove = toRemove)
	
	def gtk_attach(self, gtkContainer):
		if self.gtkContainer.get_child1() == None:
			self.gtkContainer.pack1(gtkContainer, resize=True)
		if self.gtkContainer.get_child2() == None:
			self.gtkContainer.pack2(gtkContainer, resize=True)

	def attach_child(self, child):
		if self.container1 == None:
			self.container1 = child
			self.gtkContainer.pack1(child.gtkContainer, resize=True)
			child.set_parentContainer(self)
		if self.container2 == None:
			self.container2 = child
			self.gtkContainer.pack2(child.gtkContainer, resize=True)
			child.set_parentContainer(self)
		self.gtkContainer.show_all()
	
	def set_as_current(self):
		if self.container1:
			self.container1.set_as_current()
		elif self.container2:
			self.container2.set_as_current()	
		
class HSplittedSpecialization(SplittedSpecialization):
	def __init__(self, specialized): 
		SplittedSpecialization.__init__(self, specialized)
		self.gtkContainer = gtk.HPaned()

class VSplittedSpecialization(SplittedSpecialization):
	def __init__(self, specialized):
		SplittedSpecialization.__init__(self, specialized)
		self.gtkContainer = gtk.VPaned()
		
class TopSpecialization(ContainerSpecialization):
	def __init__(self, specialized):
		ContainerSpecialization.__init__(self, specialized)
		self.gtkContainer = gtk.VBox()
		self.init_default()		
	
	def init_default(self):
		self.childContainer = BasicContainer()
		LeafSpecialization(self.childContainer)
		self.childContainer.set_parentContainer(self)
		self.gtk_attach(self.childContainer.gtkContainer)
		self.childContainer.set_as_current()
		self.gtkContainer.show_all()
	
	def gtk_attach(self, gtkContainer):
		self.gtkContainer.add(gtkContainer)
	
	def detach_child(self, childToDetach):
		childToDetach.set_parentContainer(None)
		self.gtkContainer.remove(childToDetach.gtkContainer)
		self.childContainer = None
	
	def undisplay(self, toRemove):
		self.detach_child(toRemove)
		toRemove.destroy_tree()
		self.init_default()
		
	def prepare_to_dnd(self, active, toExclude = None):
		self.childContainer.prepare_to_dnd(active, toExclude)
	
	def attach_child(self, child):
		self.childContainer = child
		self.gtkContainer.add(child.gtkContainer)
		child.set_parentContainer(self)
		self.gtkContainer.show_all()
	
	def set_as_current(self):
		self.childContainer.set_as_current()

class LeafSpecialization(ContainerSpecialization):
	current = None
	def __init__(self, specialized, gtkContainer=None):
		ContainerSpecialization.__init__(self, specialized)
		if gtkContainer == None:
			self.gtkContainer = gtk.VBox()
		else:
			self.gtkContainer = gtkContainer
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
		if self.documentView:
			self.gtkContainer.remove(self.documentView)
			self.documentView.set_parentContainer(None)
			self.documentView = None
			
		if documentView:
			documentView.set_parentContainer(self)
			self.documentView = documentView
			self.gtkContainer.add(documentView)
		self.gtkContainer.show_all()

	def get_documentView(self):
		return self.documentView
		
	def destroy_tree(self):
		if self.documentView:
			self.documentView.set_parentContainer(None)
			self.gtkContainer.remove(self.documentView)
			self.documentView = None

		self.gtkContainer = None
		CleanSpecialization(self)
	
	def undisplay(self, toRemove):
		return self.get_parentContainer().undisplay(self)
		
	def split(self, direction, newView, first = False):
		#switch basecontainer to a SplittedContainer
		currentGtkContainer = self.gtkContainer
		currentDocumentView = self.documentView
		fatherContainer = self.get_parentContainer()
		fatherContainer.gtkContainer.remove(self.gtkContainer)
		
		if direction == 0:
			HSplittedSpecialization(self)
		else:
			VSplittedSpecialization(self)
		fatherContainer.gtk_attach(self.gtkContainer)

		# create the two leaf containers
		container1 = BasicContainer()
		LeafSpecialization(container1, currentGtkContainer)
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
		
		container1.set_as_current()
	
	def set_as_current(self):
		LeafSpecialization.current = self

class DragHandler(gtk.Window):
	def __init__(self, container):
		gtk.Window.__init__(self,gtk.WINDOW_POPUP)
		self.container = container
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
		self.window.set_opacity(0)
		
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
		self.window.set_opacity(0.5)				
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

