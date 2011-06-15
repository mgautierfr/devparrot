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
	def __init__(self, child1, child2):
		AbstractContainer.__init__(self)
		self.pack1(child1, resize=True)
		self.pack2(child2, resize=True)
		child1.set_parentContainer(self)
		child2.set_parentContainer(self)
		self.show_all()
		
	def unsplit(self):
		return self.get_parentContainer().unsplit()
		
class HSplittedContainer(SplittedContainer, gtk.HPaned):
	def __init__(self, child1, child2):
		gtk.HPaned.__init__(self)
		SplittedContainer.__init__(self, child1, child2)
		self.set_border_width(0)
		
		
class VSplittedContainer(SplittedContainer, gtk.VPaned):
	def __init__(self, child1, child2):
		gtk.VPaned.__init__(self)
		SplittedContainer.__init__(self, child1, child2)
		self.set_border_width(0)

class ViewContainer(gtk.Frame, AbstractContainer):
	Horizontal = 0
	Vertical   = 1
	current = None
	def __init__(self,  child):
		gtk.Frame.__init__(self)
		AbstractContainer.__init__(self)
		self.is_splitted = False 
		self.parentContainer = None
		self.set_shadow_type(gtk.SHADOW_NONE)
		self.set_border_width(0)
		self.set_as_child(child)
		self.show_all()
		
	def set_as_child(self, child):
		if self.child:
			self.child.set_parentContainer(None)
			self.remove(self.child)
			
		if child:
			child.set_parentContainer(self)
			self.add(child)
	
	def get_child(self):
		return self.child
		

	def split(self, direction, newView):
		if self.is_splitted:
			#We only split unsplitted container
			import sys
			sys.stderr.write("Error, Trying to split a already splitted view\nThis a devparrot bug, please report it.\n")
			return
		#assert than child is a LeadContainer
		oldChild = self.child
		self.remove(oldChild)
		newContainer1 = ViewContainer(oldChild)
		newContainer2 = ViewContainer(newView)
		if direction == 0:
			self.set_as_child(HSplittedContainer(newContainer1, newContainer2))
		else:
			self.set_as_child(VSplittedContainer(newContainer1, newContainer2))
		self.is_splitted = True
		ViewContainer.current = newContainer2
		self.show_all()

	def unsplit(self):
		if not self.is_splitted:
			#Child is the final container to keep
			if self.get_parentContainer():
				# It will be attach by grandfather
				ViewContainer.to_attach = self.child
				self.remove(self.child)
				return self.get_parentContainer().unsplit()
				
		else:
			#Attach the final container instead of the splitted view
			self.remove(self.child)
			self.set_as_child(ViewContainer.to_attach)
			ViewContainer.to_attach = None
			ViewContainer.current = self
			self.is_splitted = False
			self.show_all()

class DocumentViewContainer(gtk.ScrolledWindow, AbstractContainer):
	current = None
	def __init__(self, view):
		gtk.ScrolledWindow.__init__(self)
		AbstractContainer.__init__(self)
		self.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
		self.set_view(view)

	def set_view(self, view):
		if view==None and self.view:
			self.remove(self.view)
			self.view=None
		self.view = view
		print self, "adding", self.view
		self.add(self.view)
		self.connect('set-focus-child', self.on_set_focus_child)
		self.connect("grab-focus", self.on_grab_focus)

	def get_view(self):
		return self.view

	def on_grab_focus(self, widget):
		self.view.grab_focus()
		self.show_all()
