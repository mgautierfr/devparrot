	
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