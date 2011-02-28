#    This file is part of CodeCollab.
#
#    Author: Matthieu Gautier <matthieu.gautier@mgautier.fr>
#
#    CodeCollab is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    CodeCollab is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with CodeCollab.  If not, see <http://www.gnu.org/licenses/>.
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
		self.pack1(child1)
		self.pack2(child2)
		child1.set_parentContainer(self)
		child2.set_parentContainer(self)
		self.show_all()
		
	def unsplit(self):
		return self.get_parentContainer().unsplit()
		
class HSplittedContainer(SplittedContainer, gtk.HPaned):
	def __init__(self, child1, child2):
		gtk.HPaned.__init__(self)
		SplittedContainer.__init__(self, child1, child2)
		
		
class VSplittedContainer(SplittedContainer, gtk.VPaned):
	def __init__(self, child1, child2):
		gtk.VPaned.__init__(self)
		SplittedContainer.__init__(self, child1, child2)
		

class ViewContainer(gtk.VBox, AbstractContainer):
	Horizontal = 0
	Vertical   = 1
	def __init__(self,  child):
		gtk.VBox.__init__(self)
		AbstractContainer.__init__(self)
		self.is_leafContainer = True 
		self.parentContainer = None
		self.set_as_child(child)
		self.show_all()
		
	def set_as_child(self, child):
		self.child = child
		self.child.set_parentContainer(self)
		self.add(self.child)

	def split(self, direction):
		newChild = self.child.clone()
		oldChild = self.child
		self.remove(oldChild)
		newContainer1 = ViewContainer(oldChild)
		newContainer2 = ViewContainer(newChild)
		if direction == 0:
			self.set_as_child(HSplittedContainer(newContainer1, newContainer2))
		else:
			self.set_as_child(VSplittedContainer(newContainer1, newContainer2))
		self.is_leafContainer = False
		self.show_all()

	def unsplit(self):
		if self.is_leafContainer:
			if self.get_parentContainer():
				# It will be attach by grandfather
				self.remove(self.child)
				ViewContainer.to_attach = self.child
				return self.get_parentContainer().unsplit()
				
		
		self.remove(self.child)
		self.set_as_child(ViewContainer.to_attach)
		ViewContainer.to_attach = None
		self.is_leafContainer = True
		self.show_all()