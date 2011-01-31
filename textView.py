
import gtk
from view import View

class TextView(View):
	def __init__(self):
		View.__init__(self)
		self.container = gtk.ScrolledWindow()
		self.textview = gtk.TextView()
		self.container.add(self.textview)
		self.container.show_all()

	def set_model(self, model):
		self.textview.set_buffer(model)
		pass
