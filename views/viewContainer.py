	
import gtk
from textView import TextView

class ViewContainer(gtk.VBox):
	Horizontal = 0
	Vertical   = 1
	def __init__(self, view):
		gtk.VBox.__init__(self)
		self.splitted = False
		self.contained = view
		self.add(self.contained)
		self.lastFocus = view
		self.show_all()

	def on_set_focus_child(self, container, widget, user_param = None):
		if widget:
			self.lastFocus = widget

	def split(self, direction):
		newView = TextView()
		newView.set_document(self.contained.get_document())
		self.remove(self.contained)
		newContainer1 = ViewContainer(self.contained)
		newContainer2 = ViewContainer(newView)
		self.lastFocus = newContainer1
		if direction == 0:
			self.contained = gtk.HPaned()
		else:
			self.contained = gtk.VPaned()
		self.contained.connect("set-focus-child", self.on_set_focus_child)
		self.contained.pack1(newContainer1)
		self.contained.pack2(newContainer2)
		self.add(self.contained)
		self.splitted = True
		self.show_all()
		
	def get_focused_view(self):
		if not self.splitted:
			return self.contained
		else:
			return self.lastFocus.get_focused_view()

	def get_focusedViewContainer(self):
		if not self.splitted:
			return self
		return self.lastFocus.get_focusedViewContainer()