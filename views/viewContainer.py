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

class AbstractContainer:
	def __init__(self):
		self.parentContainer = None
		pass
	
	def get_parentContainer(self) : return self.parentContainer
	def set_parentContainer(self, parent) : self.parentContainer = parent
	

class SplittedContainer(AbstractContainer):
	def __init__(self, container1, container2):
		AbstractContainer.__init__(self)
		self.pack1(container1, resize=True)
		self.pack2(container2, resize=True)
		container1.set_parentContainer(self)
		container2.set_parentContainer(self)
		self.show_all()
			
	def __unlink_child__(self, recursive=False):
		container1 = self.get_child1()
		container2 = self.get_child2()
		if container1:
			container1.set_parentContainer(None)
			self.remove(container1)
			if recursive:
				try:
					container1.__unlink_child__(recursive)
				except:pass
		if container2:
			container2.set_parentContainer(None)
			self.remove(container2)
			if recursive:
				try:
					container2.__unlink_child__(recursive)
				except:pass
	
	def prepare_to_dnd(self, active, toExclude = None):
		if self.get_child1():
			self.get_child1().prepare_to_dnd(active, toExclude)
		if self.get_child2():
			self.get_child2().prepare_to_dnd(active, toExclude)
		
	def destroy(self, child_to_not_keep, recursive=False):
		container1 = self.get_child1()
		container2 = self.get_child2()
		if container1.get_child() == None:
			child_to_keep = container2.get_child()
		else:
			if container2.get_child() == None:
				child_to_keep = container1.get_child()
			else:
				return
		self.__unlink_child__()
		if self.parentContainer:
			self.parentContainer.__unlink_child__()
			self.parentContainer.set_as_child(child_to_keep)
		
	def unsplit(self, toKeep=None, toRemove=None):
		container1 = self.get_child1()
		container2 = self.get_child2()
		child = None
		if toKeep != None:
			if container1 == toKeep:
				child = container1.get_child()
				container1.__unlink_child__()
			elif container2 == toKeep:
				child = container2.get_child()
				container2.__unlink_child__()
		elif toRemove != None:
			if container1 == toRemove:
				child = container2.get_child()
				container2.__unlink_child__()
			elif container2 == toRemove:
				child = container1.get_child()
				container1.__unlink_child__()
		if child != None:
			return self.get_parentContainer().unsplit(child)
		
class HSplittedContainer(SplittedContainer, gtk.HPaned):
	def __init__(self, container1, container2):
		gtk.HPaned.__init__(self)
		SplittedContainer.__init__(self, container1, container2)
		self.set_border_width(0)
		
		
class VSplittedContainer(SplittedContainer, gtk.VPaned):
	def __init__(self, container1, container2):
		gtk.VPaned.__init__(self)
		SplittedContainer.__init__(self, container1, container2)
		self.set_border_width(0)

class ViewContainer(gtk.EventBox, AbstractContainer):
	Horizontal = 0
	Vertical   = 1
	current = None
	def __init__(self,  child):
		gtk.EventBox.__init__(self)
		AbstractContainer.__init__(self)
		self.set_visible_window(False)
		self.is_splitted = False 
		self.parentContainer = None
		self.drag_handler = None
		self.childView = None
		self.set_as_child(child)
		self.show_all()
		
	def prepare_to_dnd(self, active, toExclude = None):
		if self.is_splitted:
			self.get_child().prepare_to_dnd(active, toExclude)
		else:
			if active:
				if toExclude and self.get_child() != toExclude:
					self.drag_handler = DragHandler(self)
			else:
				# the container can be a new created one. So the drag_handler is None
				if self.drag_handler:
					self.drag_handler.hide()
					self.drag_handler.destroy()
					self.drag_handle = None

	def set_as_child(self, child):
		if self.childView:
			self.__unlink_child__()
			
		if child:
			child.set_parentContainer(self)
			self.add(child)
			self.childView = child

	def get_child(self):
		return self.childView

	def split(self, direction, newView, first = False):
		if self.is_splitted:
			#We only split unsplitted container
			import sys
			sys.stderr.write("Error, Trying to split a already splitted view\nThis a devparrot bug, please report it.\n")
			return
		#assert than child is a LeadContainer
		oldChild = self.get_child()
		self.set_as_child(None)
		if first:
			newContainer1 = ViewContainer(newView)
			newContainer2 = ViewContainer(oldChild)
		else:
			newContainer1 = ViewContainer(oldChild)
			newContainer2 = ViewContainer(newView)
		if direction == ViewContainer.Horizontal:
			self.set_as_child(HSplittedContainer(newContainer1, newContainer2))
		else:
			self.set_as_child(VSplittedContainer(newContainer1, newContainer2))
		self.is_splitted = True
		ViewContainer.current = newContainer2
		self.show_all()

	def unsplit(self, toKeep):
		if not self.is_splitted:
			return
		#Attach the final container instead of the splitted view
		
		old_child = self.get_child()
		self.set_as_child(toKeep)
		
		old_child.__unlink_child__(recursive=True)
		
		ViewContainer.current = self
		self.is_splitted = False
		self.show_all()
			
	def __unlink_child__(self, recursive=False):
		child = self.get_child()
		if child: 
			child.set_parentContainer(None)
			self.remove(child)
			self.childView = None
			if recursive:
				try:
					child.__unlink_child__(recursive)
				except:pass	

	def delete(self):
		if self.is_splitted:
			return
		self.__unlink_child__()
		if self.parentContainer:
			self.parentContainer.unsplit(toRemove=self)

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
		r = self.container.get_allocation()
		p = self.container.window.get_origin()
		self.pos = 'center'
		self.window.move_resize(r.x+p[0],r.y+p[1],r.width,r.height)
		self.window.set_opacity(0.4)
		
	def calculate_pos(self,x,y):
		r = self.container.get_allocation()
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
		if self.container.is_splitted:
			return False
		
		r = self.container.get_allocation()
		p = self.container.window.get_origin()
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
		#we store the documentView displayed by the container cause the container could be destroy by the unsplit.
		#the documentView is the only reliable information
		currentDocumentView = self.container.get_child()
		if document.documentView.is_displayed():
			parentContainer = document.documentView.get_parentContainer()
			parentContainer.__unlink_child__()
			if parentContainer.get_parentContainer():
				parentContainer.get_parentContainer().unsplit(toRemove=parentContainer)
		if pos == 'center':
			currentDocumentView.get_parentContainer().set_as_child(document.documentView)
		if pos in ['top','bottom']:
			currentDocumentView.get_parentContainer().split(ViewContainer.Vertical, document.documentView, first=(pos=='top'))
		if pos in ['right','left']:
			currentDocumentView.get_parentContainer().split(ViewContainer.Horizontal, document.documentView, first=(pos=='left'))
