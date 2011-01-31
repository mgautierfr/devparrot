
import gtk

class TextView(object):
	def __init__(self):
		self.document = None

		self.container = gtk.VBox()
		self.label = gtk.Label()
		self.scrolledwindow = gtk.ScrolledWindow()
		self.textview = gtk.TextView()
		self.scrolledwindow.add(self.textview)
		self.container.add(self.label)
		self.container.add(self.scrolledwindow)

		self.container.child_set_property(self.label, "expand", False)
		self.container.show_all()

	def get_document(self):
		return self.document

	def on_path_changed(self, path, userData=None):
		self.label.set_text(self.document.get_title())

	def set_document(self, document):
		if self.document == document:
			return
		if self.document :
			self.document.disconnect(self.path_changed_connection)
		self.document = document
		self.textview.set_buffer(document)
		self.label.set_text(document.get_title())
		self.path_changed_connection = self.document.connect('path-changed', self.on_path_changed)


